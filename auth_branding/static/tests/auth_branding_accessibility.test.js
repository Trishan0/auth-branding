import { expect, test } from "@odoo/hoot";

import {
    bestReadableColor,
    contrastRatio,
} from "@auth_branding/js/auth_branding_accessibility";


test("contrast ratio follows WCAG reference values", () => {
    expect(contrastRatio("#000000", "#FFFFFF")).toBeCloseTo(21);
    expect(contrastRatio("#777777", "#777777")).toBeCloseTo(1);
    expect(contrastRatio("invalid", "#FFFFFF")).toBeCloseTo(21);
});

test("readable color helper selects the strongest neutral", () => {
    expect(bestReadableColor(["#FFFFFF"])).toBe("#111827");
    expect(bestReadableColor(["#111827"])).toBe("#FFFFFF");
    expect(
        contrastRatio(bestReadableColor(["#F8F9FA"]), "#F8F9FA")
    ).toBeGreaterThan(4.5);
});
