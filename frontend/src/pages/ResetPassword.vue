<template>
  <div class="reset-password-container mx-auto my-5 p-4 bg-dark rounded shadow" style="max-width: 400px;">
    <h2 class="mb-3 text-center">{{ $t('resetPassword.title') }}</h2>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ $t('common.loading') }}</span>
      </div>
      <p class="mt-2">{{ $t('resetPassword.validatingToken') }}</p>
    </div>

    <!-- Token expired or invalid -->
    <div v-else-if="tokenError" class="text-center">
      <div class="alert alert-danger" role="alert">
        <h5>{{ $t('resetPassword.tokenError') }}</h5>
        <p>{{ tokenError }}</p>
      </div>
      <RouterLink to="/recovery" class="btn btn-primary">{{ $t('resetPassword.requestNew') }}</RouterLink>
    </div>

    <!-- Password reset form -->
    <form v-else-if="tokenValid" @submit.prevent="handleResetPassword">
      <div class="mb-3">
        <label for="newPassword" class="form-label">{{ $t('resetPassword.newPasswordLabel') }}</label>
        <input 
          v-model="newPassword" 
          type="password" 
          class="form-control" 
          id="newPassword" 
          :placeholder="$t('resetPassword.newPasswordPlaceholder')" 
          required 
          minlength="6"
        />
      </div>
      
      <div class="mb-3">
        <label for="confirmPassword" class="form-label">{{ $t('resetPassword.confirmPasswordLabel') }}</label>
        <input 
          v-model="confirmPassword" 
          type="password" 
          class="form-control" 
          id="confirmPassword" 
          :placeholder="$t('resetPassword.confirmPasswordPlaceholder')" 
          required 
          minlength="6"
        />
      </div>

      <div v-if="passwordError" class="alert alert-danger" role="alert">{{ passwordError }}</div>

      <button type="submit" class="btn btn-primary w-100" :disabled="submitting">
        <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
        {{ $t('resetPassword.resetButton') }}
      </button>

      <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
        {{ successMessage }}
        <div class="mt-2">
          <RouterLink to="/login" class="btn btn-sm btn-outline-success">{{ $t('resetPassword.goToLogin') }}</RouterLink>
        </div>
      </div>
      
      <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">{{ errorMessage }}</div>
    </form>

    <div class="mt-3 text-center">
      <RouterLink to="/login" class="link-light">{{ $t('resetPassword.backToLogin') }}</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { apiPost } from '@/utils/api'
import { RouterLink } from 'vue-router'

const { t } = useI18n()
const route = useRoute()

const token = ref('')
const loading = ref(true)
const tokenValid = ref(false)
const tokenError = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const submitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

onMounted(() => {
  // Extract token from URL parameter
  token.value = route.params.token
  if (!token.value) {
    tokenError.value = t('resetPassword.noToken')
    loading.value = false
    return
  }
  
  // Token is present, mark as valid (we'll validate on submit)
  tokenValid.value = true
  loading.value = false
})

function validatePasswords() {
  passwordError.value = ''
  
  if (newPassword.value.length < 6) {
    passwordError.value = t('resetPassword.passwordTooShort')
    return false
  }
  
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = t('resetPassword.passwordsDontMatch')
    return false
  }
  
  return true
}

async function handleResetPassword() {
  if (!validatePasswords()) {
    return
  }
  
  submitting.value = true
  errorMessage.value = ''
  
  try {
    console.log('Sending reset password request with token:', token.value.substring(0, 20) + '...')
    
    const response = await apiPost('/api/auth/reset-password', {
      token: token.value,
      new_password: newPassword.value
    })
    
    console.log('Reset password response:', response)
    successMessage.value = t('resetPassword.successMsg')
    newPassword.value = ''
    confirmPassword.value = ''
    
  } catch (err) {
    console.error('Reset password error:', err)
    console.error('Error response:', err.response)
    
    if (err.response?.data?.msg) {
      const errorMsg = err.response.data.msg
      
      if (errorMsg === 'Token has expired') {
        errorMessage.value = t('resetPassword.tokenExpired')
      } else if (errorMsg === 'Invalid token') {
        errorMessage.value = t('resetPassword.invalidToken')
      } else if (errorMsg === 'User not found') {
        errorMessage.value = t('resetPassword.userNotFound')
      } else if (errorMsg === 'Missing token or new_password') {
        errorMessage.value = t('resetPassword.missingFields')
      } else {
        errorMessage.value = errorMsg
      }
    } else if (err.response?.status === 404) {
      errorMessage.value = t('resetPassword.endpointNotFound')
    } else if (err.response?.status >= 500) {
      errorMessage.value = t('resetPassword.serverError')
    } else {
      errorMessage.value = t('resetPassword.generalError')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.reset-password-container {
  background: #181818;
  color: #f0f0f0;
}

input.form-control {
  background: #232323;
  color: #f0f0f0;
  border: 1px solid #444;
}

input.form-control:focus {
  background: #232323;
  color: #fff;
  border-color: #a259ff;
  box-shadow: 0 0 0 0.2rem rgba(162,89,255,.25);
}

.alert-danger {
  background-color: #dc3545;
  border-color: #dc3545;
  color: #fff;
}

.alert-success {
  background-color: #198754;
  border-color: #198754;
  color: #fff;
}
</style>
