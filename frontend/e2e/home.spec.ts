import { expect, test } from "@playwright/test";

test("redirects the root route to the dashboard shell", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Athlete AI Coach" })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Main navigation" })).toBeVisible();
});
