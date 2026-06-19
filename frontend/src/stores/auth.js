import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userUuid = ref(localStorage.getItem('user_uuid') || '')

  const isAuthenticated = computed(() => !!token.value && !!userUuid.value)

  function setToken(newToken, newUsername, newUserUuid) {
    token.value = newToken
    username.value = newUsername
    userUuid.value = newUserUuid
    localStorage.setItem('token', newToken)
    localStorage.setItem('username', newUsername)
    localStorage.setItem('user_uuid', newUserUuid)
  }

  function clearToken() {
    token.value = ''
    username.value = ''
    userUuid.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('user_uuid')
  }

  return {
    token,
    username,
    userUuid,
    isAuthenticated,
    setToken,
    clearToken
  }
})