module.exports = {
  presets: ["next/babel"],
  plugins: [
    [
      "inline-react-svg",
      {
        svgo: {
          plugins: [
            "convertTransform",
            "removeUselessStrokeAndFill",
            "removeEditorsNSData",
            {
              cleanupIDs: {
                prefix: {
                  toString() {
                    return `${Math.random().toString(36).substr(2, 9)}`;
                  },
                },
              },
              convertTransform: false,
            },
          ],
        },
      },
    ],
    [
      "styled-components",
      {
        ssr: true,
        displayName: true,
        preprocess: false,
      },
    ],
  ],
};
