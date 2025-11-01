module.exports = {
  devServer: {
    disableHostCheck: true,
    public: process.env.HOSTNAME ? `http://${process.env.HOSTNAME}` : undefined,
    progress: false,
    proxy: {
      '^/api': {
        target: `http://${process.env.VUE_APP_API_URL}`,
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
      },
      '^/socket.io': {
        target: 'http://result',
        changeOrigin: true,
        secure: false,
        ws: true,
        logLevel: 'debug',
      },
    },
  },
};
