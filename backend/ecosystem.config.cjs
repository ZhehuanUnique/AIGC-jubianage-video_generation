module.exports = {
  apps: [{
    name: 'aigc-backend',
    script: 'python',
    args: ['-m', 'uvicorn', 'backend.api:app', '--host', '0.0.0.0', '--port', '8001'],
    cwd: 'C:\\Users\\Administrator\\Desktop\\AIGC-jubianage-video_generation\\backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    exec_mode: 'fork',
    env: {
      NODE_ENV: 'production',
      PORT: '8001'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
}

