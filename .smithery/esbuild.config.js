// Custom esbuild configuration for Smithery
export default {
  external: ['@modelcontextprotocol/sdk', '@modelcontextprotocol/sdk/server/mcp.js'],
  format: 'esm',
  platform: 'node',
  target: 'node16',
  bundle: true,
  minify: false,
  sourcemap: true,
  resolveExtensions: ['.ts', '.js', '.json'],
};
