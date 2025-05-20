import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userName = computed(() => user.value?.name)
  const userId = computed(() => user.value?.id)

  // Actions
  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUser(newUser) {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function login(userData) {
    setToken(userData.token)
    setUser(userData.user)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    // Opcional: redirecionar para a página de login ou home
    // router.push('/login'); 
  }

  return {
    token,
    user,
    isAuthenticated,
    userName,
    userId,
    login,
    logout,
    setToken, // Exposto caso precise ser chamado diretamente em algum ponto
    setUser   // Exposto caso precise ser chamado diretamente em algum ponto
  }
})
