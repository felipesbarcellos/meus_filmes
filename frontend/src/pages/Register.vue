<template>
  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-sm-10 col-md-8 col-lg-7">
        <div class="card bg-dark text-light shadow-lg">
          <div class="card-body p-4 p-md-5">
            <h2 class="card-title text-center mb-4">Criar Conta</h2>
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label for="name" class="form-label">Nome</label>
                <input type="text" id="name" class="form-control form-control-lg bg-secondary text-light border-secondary" v-model="name" required />
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" id="email" class="form-control form-control-lg bg-secondary text-light border-secondary" v-model="email" required />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Senha</label>
                <input type="password" id="password" class="form-control form-control-lg bg-secondary text-light border-secondary" v-model="password" required />
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirmar Senha</label>
                <input type="password" id="confirmPassword" class="form-control form-control-lg bg-secondary text-light border-secondary" v-model="confirmPassword" required />
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="isLoading">
                  {{ isLoading ? 'Registrando...' : 'Registrar' }}
                </button>
              </div>
              <p v-if="error" class="text-danger mt-3 text-center">{{ error }}</p>
              <p v-if="successMessage" class="text-success mt-3 text-center">{{ successMessage }}</p>
            </form>
            <hr class="my-4 border-secondary">
            <div class="text-center">
              <p class="mb-2">Já tem uma conta?</p>
              <button @click="goToLogin" class="btn btn-outline-light">Faça login aqui</button>
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
import { useAuthStore } from '@/stores/auth' // Importar o store Pinia
import { apiPost } from '@/utils/api'

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const router = useRouter()
const authStore = useAuthStore() // Usar o store Pinia

async function handleRegister() {
  isLoading.value = true
  error.value = ''
  successMessage.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = 'As senhas não coincidem.'
    isLoading.value = false
    return
  }

  try {
    const data = await apiPost('/api/auth/register', {
      name: name.value,
      email: email.value,
      password: password.value,
    })
    if (!data || data.error || data.msg) {
      throw new Error(data.msg || data.error || 'Falha no registro.')
    }
    // Após o registro bem-sucedido, faz o login automaticamente
    authStore.login(data) // Usa a action do store Pinia para logar o usuário
    successMessage.value = 'Registro bem-sucedido! Redirecionando...'
    setTimeout(() => {
      router.push('/') // Redireciona para a home
    }, 2000)
  } catch (err) {
    error.value = err.message
    console.error('Erro no registro:', err)
  } finally {
    isLoading.value = false
  }
}

function goToLogin() {
  router.push('/login')
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

/* Custom styles for dark theme form controls */
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

</style>
