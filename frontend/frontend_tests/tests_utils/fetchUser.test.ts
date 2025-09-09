import { fetchUser } from "@/utils/fetchUser";

describe("fetchUser", () => {
  it("should be defined", () => {
    expect(fetchUser).toBeDefined();
  });

  it("should be a function", () => {
    expect(typeof fetchUser).toBe("function");
  });
});