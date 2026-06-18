<template>
  <div class="login-overlay">
    <div class="anime-background">
      <div class="particle" v-for="i in 50" :key="i" :style="getParticleStyle(i)"></div>
    </div>

    <div class="login-modal">
      <div class="modal-header">
        <h1 class="title">🌸 欢迎来到 Data Agent</h1>
        <p class="subtitle">智能数据查询助手</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            required
            class="input-field"
          />
        </div>

        <button
          type="submit"
          :disabled="loading || username.length < 3"
          class="login-button"
        >
          <span v-if="!loading">进入聊天</span>
          <span v-else class="loading-text">
            <span class="dot">.</span>
            <span class="dot">.</span>
            <span class="dot">.</span>
          </span>
        </button>

        <p v-if="error" class="error-message">{{ error }}</p>
        <p v-if="username.length > 0 && username.length < 3" class="warning-message">用户名长度不能少于3个字符</p>
      </form>

      <div class="anime-decoration">
        <div class="sparkle" v-for="i in 8" :key="i"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()
const username = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await api.post('/user/login', {
      username: username.value
    })

    authStore.setToken(response.data.token, username.value)
  } catch (err) {
    error.value = err.response?.data?.message || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}

const getParticleStyle = (index) => {
  const size = Math.random() * 6 + 2
  const left = Math.random() * 100
  const animationDelay = Math.random() * 5
  const animationDuration = Math.random() * 10 + 10

  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${animationDelay}s`,
    animationDuration: `${animationDuration}s`
  }
}
</script>

<style scoped>
.login-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 30%, #0369a1 60%, #075985 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow: hidden;
}

.anime-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: float linear infinite;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

@keyframes float {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(720deg);
    opacity: 0;
  }
}

.login-modal {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px;
  width: 90%;
  max-width: 420px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2),
              0 0 100px rgba(14, 165, 233, 0.3);
  animation: modalAppear 0.6s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

@keyframes modalAppear {
  0% {
    transform: scale(0.8) translateY(30px);
    opacity: 0;
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.modal-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 50%, #22d3ee 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  animation: titleGlow 2s ease-in-out infinite alternate;
}

@keyframes titleGlow {
  0% {
    filter: drop-shadow(0 0 5px rgba(14, 165, 233, 0.5));
  }
  100% {
    filter: drop-shadow(0 0 15px rgba(34, 211, 238, 0.8));
  }
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-left: 4px;
}

.input-field {
  padding: 16px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f9fafb;
}

.input-field:focus {
  outline: none;
  border-color: #0ea5e9;
  background: white;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
  transform: translateY(-2px);
}

.input-field::placeholder {
  color: #9ca3af;
}

.login-button {
  padding: 16px 32px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.4);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.login-button:hover::before {
  left: 100%;
}

.loading-text {
  display: flex;
  justify-content: center;
  gap: 4px;
}

.dot {
  animation: dotPulse 1.4s infinite;
}

.dot:nth-child(1) {
  animation-delay: 0s;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotPulse {
  0%, 80%, 100% {
    opacity: 0.3;
  }
  40% {
    opacity: 1;
  }
}

.error-message {
  color: #ef4444;
  font-size: 14px;
  text-align: center;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  animation: shake 0.5s ease-in-out;
}

.warning-message {
  color: #f59e0b;
  font-size: 14px;
  text-align: center;
  padding: 12px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 8px;
  animation: fadeIn 0.3s ease-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

.anime-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
}

.sparkle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #67e8f9 0%, #0ea5e9 100%);
  border-radius: 50%;
  animation: sparkle 2s ease-in-out infinite;
}

.sparkle:nth-child(1) { top: 20%; left: 20%; animation-delay: 0s; }
.sparkle:nth-child(2) { top: 40%; left: 80%; animation-delay: 0.3s; }
.sparkle:nth-child(3) { top: 60%; left: 30%; animation-delay: 0.6s; }
.sparkle:nth-child(4) { top: 80%; left: 70%; animation-delay: 0.9s; }
.sparkle:nth-child(5) { top: 10%; left: 60%; animation-delay: 1.2s; }
.sparkle:nth-child(6) { top: 70%; left: 10%; animation-delay: 1.5s; }
.sparkle:nth-child(7) { top: 30%; left: 50%; animation-delay: 1.8s; }
.sparkle:nth-child(8) { top: 50%; left: 90%; animation-delay: 2.1s; }

@keyframes sparkle {
  0%, 100% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>