// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // 静态站点生成配置
  target: 'static',
  ssr: false,
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],
  css: ['~/assets/css/main.css'],
  devServer: {
    port: 3001,
    host: '0.0.0.0'
  },
  // 配置Nitro确保静态文件正确服务
  nitro: {
    prerender: {
      crawlLinks: false
    },
    // 确保静态文件优先服务
    publicAssets: [
      {
        baseURL: '/',
        dir: 'public',
        maxAge: 31536000
      }
    ]
  },
  // 路由配置
  router: {
    base: '/'
  },
  runtimeConfig: {
    public: {
      backendUrl: process.env.BACKEND_URL || 'http://localhost:8000'
    }
  },
  app: {
    head: {
      title: '剧变时代 - AI 视频生成',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '基于即梦 AI 的视频生成平台' }
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }
      ]
    }
  }
})

