# MCP Local Testing Plan

This plan outlines the steps to test the MCP server locally using the Smithery playground.

## Todo

- [x] Run `npm install` to ensure all dependencies are installed.
- [ ] Run `npm run dev` to start the Smithery playground.
- [ ] Verify that the playground opens in the browser.
- [ ] Test the MCP server's functionality within the playground.
- [x] **Debug and fix the "Resource not found" error.**
  - [x] Investigated the Ghost API initialization in `src/ghostApi.ts`.
  - [x] Corrected the `makeGhostApi` function to ensure the API version is passed correctly.