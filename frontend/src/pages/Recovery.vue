<template>
  <div class="recovery-container mx-auto my-5 p-4 bg-dark rounded shadow" style="max-width: 400px;">
    <h2 class="mb-3 text-center">{{ $t('recovery.title') }}</h2>
    <form @submit.prevent="handleRecovery">
      <div class="mb-3">
        <label for="email" class="form-label">{{ $t('recovery.emailLabel') }}</label>
        <input v-model="email" type="email" class="form-control" id="email" :placeholder="$t('recovery.emailPlaceholder')" required />
      </div>
      <button type="submit" class="btn btn-primary w-100" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
        {{ $t('recovery.sendButton') }}
      </button>
      <div v-if="message" class="alert alert-success mt-3" role="alert">{{ message }}</div>
      <div v-if="error" class="alert alert-danger mt-3" role="alert">{{ error }}</div>
    </form>
    <div class="mt-3 text-center">
      <RouterLink to="/login" class="link-light">{{ $t('recovery.backToLogin') }}</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiPost } from '@/utils/api'
import { RouterLink } from 'vue-router'

const { t } = useI18n()
const email = ref('')
const loading = ref(false)
const message = ref('')
const error = ref('')

async function handleRecovery() {
  loading.value = true
  message.value = ''
  error.value = ''
  try {
    await apiPost('/api/auth/recovery', { email: email.value })
    message.value = t('recovery.successMsg')
  } catch (err) {
    message.value = t('recovery.successMsg')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recovery-container {
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
</style>
