const path = require("path");

module.exports = {
  stories: ["../src/**/*.stories.@(js|mdx)"],
  addons: ["@storybook/addon-storysource"],
  webpackFinal: async (config) => {
    // Add src to imports (so this works with app webpack config
    config.resolve.modules.push(path.resolve(__dirname, "../src"));
    return config;
  },
};
