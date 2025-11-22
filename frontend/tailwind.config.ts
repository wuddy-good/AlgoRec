import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      screens: {
        'xs': '320px',    // дуже маленькі телефони
        'sm': '640px',    // телефони
        'md': '768px',    // планшети
        'lg': '1024px',   // маленькі ноутбуки
        'xl': '1280px',   // великі ноутбуки
        '2xl': '1536px',  // великі монітори
      },
      width: {
        'sidebar': '235px',
      },
      colors: {
        brand: {
          orange: '#E16A17',  // важливий колір для кнопок
          blue: '#026E89',    // важливий колір для кнопок
        },
        accent: {
          orange: '#E16A17',  // основний акцентний колір
          'orange-light': '#F4A460',  // світліший варіант
          'orange-dark': '#CD853F',   // темніший варіант
          blue: '#026E89',    // основний акцентний колір
          'blue-light': '#4A9FD1',    // світліший варіант
          'blue-dark': '#015A73',     // темніший варіант
        },
        text: {
          primary: '#111827',  // основний колір для тексту
          'primary-light': '#6B7280',  // світліший варіант
          'primary-dark': '#000000',   // темніший варіант
        },
        background: {
          'blue-light': '#CDF4FE',  // світло-блакитний для блоків
          'blue-lighter': '#E6F8FF',  // ще світліший варіант
          'blue-lightest': '#F0FBFF',  // найсвітліший варіант
        },
        rating: {
          star: '#F9DF16',  // жовтий для рейтингу
          'star-light': '#FEF3C7',  // світліший варіант
          'star-dark': '#F59E0B',   // темніший варіант
        },
        gray: {
          medium: '#767676',  // середній сірий
          light: '#949494',   // світлий сірий
          'medium-dark': '#5A5A5A',  // темніший варіант
          'light-dark': '#7A7A7A',  // темніший світлий
          'very-light': '#F4F4F4',  // дуже світлий сірий
          'very-light-dark': '#E5E5E5',  // темніший дуже світлий
          'lighter': '#E0E0E0',  // світліший сірий
        },
        white: {
          pure: '#FFFFFF',  // класичний білий
          'off-white': '#FAFAFA',  // трохи тепліший білий
        }
      },
    },
  },
  plugins: [],
}

export default config