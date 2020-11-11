module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    ...(process.env.NODE_ENV === 'production'
      ? {
          '@fullhuman/postcss-purgecss': {
            content: [
              './pages/**/*.{js,jsx,ts,tsx,mdx}',
              './components/**/*.{js,jsx,ts,tsx}',
              './layout/**/*.{js,jsx,ts,tsx}',
              './markdown/**/*.{js,jsx,ts,tsx,mdx}',
            ],
            whitelist: ['hero', 'prose', 'image-offset'],
            defaultExtractor: (content) => content.match(/[\w-/:]+(?<!:)/g) || [],
          },
        }
      : {}),
  },
}
