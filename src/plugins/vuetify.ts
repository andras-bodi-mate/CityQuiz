
import { createVuetify } from 'vuetify'
import { VIconBtn } from 'vuetify/labs/VIconBtn'
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'system',
  },
  components: {
    VIconBtn
  }
})
