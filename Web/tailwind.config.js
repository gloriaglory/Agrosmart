/** @type {import('tailwindcss').Config} */
export default {
 content: [
  "./index.html",
  "./src/**/*.{js,ts,jsx,tsx}",
],
theme: {
  extend: {
    extend: {
      colors: {
        primary: '#16a34a',     
        secondary: '#bbf7d0',  
      },
    },  
  },
},
plugins: [],

}

