import base64
import binascii
import json
import math

from odoo import _, fields, models
from odoo.exceptions import UserError


class AuthBrandingImportWizard(models.TransientModel):
    _name = "auth.branding.import.wizard"
    _description = "Import Authentication Branding"
    _check_company_auto = True

    MAX_FILE_SIZE = 16 * 1024 * 1024
    MAX_ASSET_SIZE = 8 * 1024 * 1024

    state = fields.Selection(
        [("upload", "Upload"), ("review", "Review")],
        default="upload",
        required=True,
    )
    config_id = fields.Many2one(
        "auth.branding.config", required=True, check_company=True
    )
    company_id = fields.Many2one(
        "res.company", related="config_id.company_id", readonly=True
    )
    import_file = fields.Binary(string="Branding JSON File", required=True)
    import_filename = fields.Char(string="Filename")
    import_summary = fields.Text(readonly=True)

    def _decode_payload(self):
        self.ensure_one()
        try:
            raw = base64.b64decode(self.import_file or b"", validate=True)
        except (ValueError, binascii.Error) as error:
            raise UserError(_("The uploaded file is not valid base64 data.")) from error
        if len(raw) > self.MAX_FILE_SIZE:
            raise UserError(_("The branding import file cannot exceed 16 MB."))
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise UserError(_("Upload a valid UTF-8 JSON branding export.")) from error
        if not isinstance(payload, dict):
            raise UserError(_("The branding export must contain a JSON object."))
        return payload

    def _normalize_payload(self, payload):
        config_model = self.env["auth.branding.config"]
        if payload.get("format") != config_model.EXPORT_FORMAT:
            raise UserError(_("This file is not an Auth Branding export."))
        if payload.get("schema_version") != config_model.EXPORT_SCHEMA_VERSION:
            raise UserError(
                _(
                    "Unsupported branding schema version: %(version)s.",
                    version=payload.get("schema_version"),
                )
            )

        raw_settings = payload.get("settings", {})
        raw_assets = payload.get("assets", {})
        if not isinstance(raw_settings, dict) or not isinstance(raw_assets, dict):
            raise UserError(_("Branding settings and assets must be JSON objects."))

        allowed_settings = set(config_model.VERSIONED_FIELDS) - set(
            config_model.BINARY_FIELDS
        )
        settings = {
            field_name: False if value is None else value
            for field_name, value in raw_settings.items()
            if field_name in allowed_settings
        }
        for field_name, value in settings.items():
            field = config_model._fields[field_name]
            valid = True
            if field.type == "boolean":
                valid = isinstance(value, bool)
            elif field.type == "integer":
                valid = isinstance(value, int) and not isinstance(value, bool)
            elif field.type == "float":
                valid = (
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                )
            elif field.type in {"char", "text", "selection"}:
                valid = value is False or isinstance(value, str)
            if valid and field.type == "selection" and value is not False:
                valid = value in dict(field.selection)
            if field.required and value is False:
                valid = False
            if not valid:
                raise UserError(
                    _(
                        "Invalid value for branding field %(field)s.",
                        field=field.string,
                    )
                )
        ignored_fields = sorted(set(raw_settings) - allowed_settings)
        assets = {}
        for field_name in config_model.BINARY_FIELDS:
            if field_name not in raw_assets:
                continue
            encoded_value = raw_assets.get(field_name)
            if not encoded_value:
                assets[field_name] = False
                continue
            if not isinstance(encoded_value, str):
                raise UserError(
                    _("Asset %(field)s must be base64 text.", field=field_name)
                )
            try:
                decoded = base64.b64decode(encoded_value, validate=True)
            except (ValueError, binascii.Error) as error:
                raise UserError(
                    _("Asset %(field)s is not valid base64 data.", field=field_name)
                ) from error
            if len(decoded) > self.MAX_ASSET_SIZE:
                raise UserError(
                    _("Asset %(field)s cannot exceed 8 MB.", field=field_name)
                )
            assets[field_name] = encoded_value

        return {
            "settings": settings,
            "assets": assets,
            "source_company": str(payload.get("company") or ""),
            "ignored_fields": ignored_fields,
        }

    def action_review(self):
        self.ensure_one()
        normalized = self._normalize_payload(self._decode_payload())
        asset_count = sum(bool(value) for value in normalized["assets"].values())
        ignored = normalized["ignored_fields"]
        summary_lines = [
            _(
                "Source company: %(company)s",
                company=normalized["source_company"] or _("Unknown"),
            ),
            _("Settings ready to import: %(count)s", count=len(normalized["settings"])),
            _("Embedded assets ready to import: %(count)s", count=asset_count),
        ]
        if ignored:
            summary_lines.append(
                _("Ignored unsupported fields: %(fields)s", fields=", ".join(ignored))
            )
        self.write(
            {
                "state": "review",
                "import_summary": "\n".join(summary_lines),
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_back(self):
        self.ensure_one()
        self.state = "upload"
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_apply(self):
        self.ensure_one()
        if self.state != "review":
            raise UserError(_("Review the import before applying it."))
        normalized = self._normalize_payload(self._decode_payload())
        values = {**normalized["settings"], **normalized["assets"]}
        self.config_id.write(values)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Branding imported as draft"),
                "message": _("Review the preview, then publish when you are ready."),
                "type": "success",
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }
