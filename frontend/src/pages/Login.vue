<template>
  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-sm-10 col-md-8 col-lg-5">
        <div class="card bg-dark text-light shadow-lg">
          <div class="card-body p-4 p-md-5">
            <h2 class="card-title text-center mb-4">Login</h2>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" id="email" class="form-control form-control-lg bg-secondary text-light border-secondary" v-model="email" required />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Senha</label>
                <input type="password" id="password" class="form-control form-control-lg bg-secondary text-light border-secondary" v-model="password" required />
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="isLoading">
                  {{ isLoading ? 'Entrando...' : 'Entrar' }}
                </button>
              </div>
              <p v-if="error" class="text-danger mt-3 text-center">{{ error }}</p>
            </form>
            <hr class="my-4 border-secondary">
            <div class="text-center">
              <p class="mb-2">Não tem uma conta?</p>
              <button @click="goToRegister" class="btn btn-outline-light">Crie uma aqui</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiPost } from '@/utils/api'

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const router = useRouter()
const authStore = useAuthStore()

async function handleLogin() {
  isLoading.value = true
  error.value = ''
  try {
    const data = await apiPost('/api/auth/login', {
      email: email.value,
      password: password.value,
    })
    if (!data || data.error || data.msg) {
      throw new Error(data.msg || data.error || 'Falha no login')
    }
    authStore.login(data) // Usa a action do store Pinia
    router.push('/')
  } catch (err) {
    error.value = err.message
    console.error('Erro no login:', err)
  } finally {
    isLoading.value = false
  }
}

function goToRegister() {
  router.push('/registrar')
}
</script>

<style scoped>
/* Minimal custom styles - Bootstrap handles most of it */
.card {
  border: none; /* Remove default card border if not desired */
  border-radius: 0.75rem; /* Custom border radius */
}

.form-control::placeholder {
  color: #adb5bd; /* Lighter placeholder text for dark inputs */
}

.btn-primary {
  background-color: #a259ff;
  border-color: #a259ff;
}

.btn-primary:hover, .btn-primary:focus {
  background-color: #8e4de6;
  border-color: #8e4de6;
}

/* Ensure custom focus glow matches primary color if desired */
.form-control:focus {
  border-color: #a259ff;
  box-shadow: 0 0 0 0.25rem rgba(162, 89, 255, 0.25);
}

/* Custom styles for dark theme form controls, consistent with Register.vue */
.form-control.bg-secondary {
  background-color: #343a40 !important; /* Darker background for inputs */
  color: #f8f9fa !important; /* Light text for inputs */
  border-color: #495057 !important; /* Slightly lighter border for inputs */
}

.form-control.bg-secondary:focus {
  background-color: #343a40 !important;
  color: #f8f9fa !important;
  border-color: #a259ff; /* Keep focus color */
}

/* Removed all previous custom CSS like .login-container, .login-card, .input-group, etc. */
/* .login-container { ... } */
/* .login-card { ... } */
/* .login-card h2 { ... } */
/* .input-group { ... } */
/* .input-group label { ... } */
/* .input-group input { ... } */
/* .input-group input:focus { ... } */
/* .btn.login-btn { ... } */
/* .btn.login-btn:hover:not(:disabled) { ... } */
/* .btn:disabled { ... } */ /* Bootstrap handles this */
/* .error-message { ... } */ /* Replaced with .text-danger */
/* .alternative-action { ... } */
/* .alternative-action p { ... } */
/* .btn.register-link-btn { ... } */
/* .btn.register-link-btn:hover { ... } */
</style>
