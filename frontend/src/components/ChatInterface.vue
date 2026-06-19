<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="header-content">
        <div class="avatar">
          <span class="avatar-icon">🤖</span>
        </div>
        <div class="header-info">
          <h2 class="chat-title">Data Agent</h2>
          <p class="chat-subtitle">智能数据查询助手</p>
        </div>
      </div>
      <button @click="handleLogout" class="logout-button">
        <span class="logout-icon">🚪</span>
        <span>退出</span>
      </button>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role]"
      >
        <div class="message-avatar">
          <span v-if="message.role === 'user'" class="user-avatar">
            {{ authStore.username?.charAt(0).toUpperCase() }}
          </span>
          <span v-else class="bot-avatar">🤖</span>
        </div>
        <div class="message-content">
          <div class="message-bubble">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>

      <div v-if="isTyping" class="message assistant">
        <div class="message-avatar">
          <span class="bot-avatar">🤖</span>
        </div>
        <div class="message-content">
          <div class="message-bubble">
            <div v-if="progressSteps.length > 0" class="progress-container">
              <div
                v-for="(step, index) in progressSteps"
                :key="index"
                :class="['progress-step', step.status]"
              >
                <div class="progress-icon">
                  <span v-if="step.status === 'running'" class="spinner"></span>
                  <span v-else-if="step.status === 'success'" class="success-icon">✓</span>
                  <span v-else-if="step.status === 'error'" class="error-icon">✗</span>
                </div>
                <div class="progress-text">{{ step.step }}</div>
              </div>
            </div>
            <div v-else class="typing-indicator">
              <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-container">
      <form @submit.prevent="handleSendMessage" class="input-form">
        <div class="input-wrapper">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="输入您的问题..."
            class="chat-input"
            :disabled="isTyping"
            ref="inputField"
          />
          <button
            type="submit"
            :disabled="!inputMessage.trim() || isTyping"
            class="send-button"
          >
            <span class="send-icon">📤</span>
          </button>
        </div>
      </form>
      <div class="input-hint">
        <span class="hint-text">💡 提示：您可以询问数据相关的任何问题</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()
const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const progressSteps = ref([])
const messagesContainer = ref(null)
const inputField = ref(null)

const formatMessage = (content) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || isTyping.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    timestamp: Date.now()
  }

  messages.value.push(userMessage)
  const query = inputMessage.value
  inputMessage.value = ''
  isTyping.value = true
  progressSteps.value = []

  await scrollToBottom()

  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ query })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let assistantMessage = {
      role: 'assistant',
      content: '',
      timestamp: Date.now()
    }
    messages.value.push(assistantMessage)

    let hasError = false

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            isTyping.value = false
            progressSteps.value = []
            await scrollToBottom()
            return
          }
          try {
            const parsed = JSON.parse(data)

            // 处理进度信息
            if (parsed.type === 'progress') {
              const existingStepIndex = progressSteps.value.findIndex(
                step => step.step === parsed.step
              )

              if (existingStepIndex >= 0) {
                // 更新现有步骤状态
                progressSteps.value[existingStepIndex] = {
                  step: parsed.step,
                  status: parsed.status
                }
              } else {
                // 添加新步骤
                progressSteps.value.push({
                  step: parsed.step,
                  status: parsed.status
                })
              }

              // 如果是错误状态，终止处理
              if (parsed.status === 'error') {
                hasError = true
                assistantMessage.content += `\n❌ ${parsed.step} 执行失败`
              }
            } else {
              // 处理普通内容
              assistantMessage.content += parsed.content || ''
            }

            await scrollToBottom()
          } catch (e) {
            console.error('解析响应失败:', e)
          }
        }
      }
    }

    isTyping.value = false
    progressSteps.value = []
    await scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误，请稍后重试。',
      timestamp: Date.now()
    })
    isTyping.value = false
    progressSteps.value = []
    await scrollToBottom()
  }
}

const handleLogout = () => {
  authStore.clearToken()
  window.location.reload()
}

onMounted(() => {
  inputField.value?.focus()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.3);
  position: relative;
  z-index: 10;
}

.chat-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  pointer-events: none;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  animation: avatarPulse 3s ease-in-out infinite;
}

@keyframes avatarPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(255, 255, 255, 0);
  }
}

.avatar-icon {
  font-size: 24px;
  animation: iconBounce 2s ease-in-out infinite;
}

@keyframes iconBounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

.header-info {
  color: white;
}

.chat-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-subtitle {
  font-size: 12px;
  opacity: 0.9;
  font-weight: 500;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.logout-icon {
  font-size: 16px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  scroll-behavior: smooth;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(14, 165, 233, 0.3);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(14, 165, 233, 0.5);
}

.message {
  display: flex;
  gap: 12px;
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.user-avatar {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}

.bot-avatar {
  background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%);
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.3);
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 70%;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
  position: relative;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}

.message.assistant .message-bubble {
  background: white;
  color: #1f2937;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-text {
  white-space: pre-wrap;
}

.message-text code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.message-text strong {
  font-weight: 600;
}

.message-time {
  font-size: 11px;
  color: #9ca3af;
  padding: 0 4px;
}

.typing-indicator {
  padding: 12px 16px;
  background: white;
  border-radius: 18px;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots .dot {
  width: 8px;
  height: 8px;
  background: #0ea5e9;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dots .dot:nth-child(1) {
  animation-delay: 0s;
}

.typing-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingBounce {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 0;
}

.progress-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(14, 165, 233, 0.05);
  border-radius: 8px;
  transition: all 0.3s ease;
  animation: stepSlideIn 0.3s ease-out;
}

@keyframes stepSlideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.progress-step.running {
  background: rgba(14, 165, 233, 0.1);
  border-left: 3px solid #0ea5e9;
}

.progress-step.success {
  background: rgba(16, 185, 129, 0.1);
  border-left: 3px solid #10b981;
}

.progress-step.error {
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #ef4444;
}

.progress-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #0ea5e9;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.success-icon {
  color: #10b981;
  font-weight: bold;
  font-size: 14px;
  animation: successPop 0.3s ease-out;
}

@keyframes successPop {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.error-icon {
  color: #ef4444;
  font-weight: bold;
  font-size: 14px;
  animation: errorShake 0.3s ease-out;
}

@keyframes errorShake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-3px);
  }
  75% {
    transform: translateX(3px);
  }
}

.progress-text {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
  flex: 1;
}

.progress-step.running .progress-text {
  color: #0ea5e9;
}

.progress-step.success .progress-text {
  color: #10b981;
}

.progress-step.error .progress-text {
  color: #ef4444;
}

.chat-input-container {
  padding: 20px 24px;
  background: white;
  border-top: 1px solid #e5e7eb;
  position: relative;
  z-index: 10;
}

.input-form {
  display: flex;
  gap: 12px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  flex: 1;
  position: relative;
}

.chat-input {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 24px;
  font-size: 15px;
  transition: all 0.3s ease;
  background: #f9fafb;
}

.chat-input:focus {
  outline: none;
  border-color: #0ea5e9;
  background: white;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}

.chat-input::placeholder {
  color: #9ca3af;
}

.chat-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-button {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.send-button:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
}

.send-button:active:not(:disabled) {
  transform: scale(0.95);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.send-icon {
  font-size: 20px;
  animation: sendIconFloat 2s ease-in-out infinite;
}

@keyframes sendIconFloat {
  0%, 100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(2px);
  }
}

.input-hint {
  margin-top: 12px;
  text-align: center;
}

.hint-text {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}

@media (max-width: 768px) {
  .chat-header {
    padding: 16px;
  }

  .chat-messages {
    padding: 16px;
  }

  .message-content {
    max-width: 85%;
  }

  .chat-input-container {
    padding: 16px;
  }

  .logout-button {
    padding: 8px 16px;
  }

  .logout-button span:last-child {
    display: none;
  }
}
</style>