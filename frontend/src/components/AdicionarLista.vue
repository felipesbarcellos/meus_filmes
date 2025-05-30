<template>
  <div class="adicionar-lista">
    <h5 class="mb-3">Adicionar:</h5>
    <ul class="list-unstyled d-flex flex-wrap gap-2">
      <li v-for="list in mainLists" :key="list.id">
        <button class="btn btn-outline-primary" @click="list.name === 'Assistidos' ? handleClick('assistidos') : addToMainList(list)">{{ list.name }}</button>
      </li>
      <li>
        <button class="btn btn-outline-secondary" @click="handleClick('outra')">Outra</button>
      </li>
    </ul>

    <!-- Entrada de data para Assistidos -->
    <div v-if="showDateInput" class="mt-3">
      <label class="form-label">Data assistido:</label>
      <input type="date" v-model="watchedDate" class="form-control bg-dark text-light border-secondary" />
      <button class="btn btn-success mt-2" @click="confirmWatched">Confirmar</button>
    </div>

    <!-- Seleção de lista personalizada -->
    <div v-if="showUserLists" class="mt-3">
      <label class="form-label">Selecione a lista:</label>
      <select v-model="selectedListId" class="form-select bg-dark text-light border-secondary mb-2">
        <option v-for="list in userLists" :key="list.id" :value="list.id">{{ list.name }}</option>
      </select>
      <button class="btn btn-primary" @click="confirmAddToList">Adicionar</button>
    </div>

    <div v-if="successMsg" class="alert alert-success mt-2">{{ successMsg }}</div>
    <div v-if="errorMsg" class="alert alert-danger mt-2">{{ errorMsg }}</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { apiGet, apiPost } from '@/utils/api'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  movieId: { type: [String, Number], required: true }
})

const authStore = useAuthStore()
const userLists = ref([])
const mainLists = ref([])
const selectedListId = ref(null)
const showUserLists = ref(false)
const showDateInput = ref(false)
const watchedDate = ref(new Date().toISOString().split('T')[0])
const successMsg = ref('')
const errorMsg = ref('')
const { t } = useI18n()

function resetStates() {
  showUserLists.value = false
  showDateInput.value = false
  successMsg.value = ''
  errorMsg.value = ''
}

function handleClick(type) {
  resetStates()
  if (type === 'outra') {
    showUserLists.value = true
    fetchUserLists()
  } else if (type === 'assistidos') {
    showDateInput.value = true
  }
  setTimeout(() => {
    successMsg.value = ''
    errorMsg.value = ''
  }, 4000)
}

async function fetchUserLists() {
  if (!authStore.isAuthenticated) return
  try {
    const data = await apiGet('/api/lists/')
    userLists.value = data
    mainLists.value = data.filter(l => l.is_main)
    if (userLists.value.length > 0) selectedListId.value = userLists.value[0].id
  } catch (e) {
    errorMsg.value = e.message
  }
}

onMounted(fetchUserLists)

async function addToMainList(list) {
  resetStates()
  try {
    const resp = await apiPost(`/api/lists/add_movie`, {
      list_id: list.id,
      tmdb_id: props.movieId
    })
    successMsg.value = resp.msg || 'Adicionado com sucesso!'
  } catch (e) {
    errorMsg.value = e.message
  }
  setTimeout(() => {
    successMsg.value = ''
    errorMsg.value = ''
  }, 4000)
}

async function addToSpecialList(type) {
  let listType
  if (type === 'favoritos') listType = 'Favoritos'
  if (type === 'queroAssistir') listType = 'Quero ver'
  if (!listType) return
  try {
    // Busca a lista especial do usuário
    const data = await apiGet('/api/lists/')
    const specialList = data.find(l => l.name === listType)
    if (!specialList) {
      errorMsg.value = `Não foi encontrada a lista (${listType}) para este usuário.`
      return
    }
    const resp = await apiPost(`/api/lists/add_movie`, {
      list_id: specialList.id,
      tmdb_id: props.movieId
    })
    successMsg.value = resp.msg || 'Adicionado com sucesso!'
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function confirmAddToList() {
  if (!selectedListId.value) {
    errorMsg.value = t('movieDetails.selectListError') || 'Selecione uma lista.'
    return
  }
  try {
    const resp = await apiPost(`/api/lists/add_movie`, {
      list_id: selectedListId.value,
      tmdb_id: props.movieId
    })
    successMsg.value = resp.msg || t('movieDetails.addToListSuccess') || 'Adicionado com sucesso!'
  } catch (e) {
    errorMsg.value = e.message
  }
}

async function confirmWatched() {
  try {
    const data = await apiPost(`/api/movie/watched/`, {
      tmdb_id: props.movieId,
      watched_at: watchedDate.value
    })
    // Mensagem amigável independente do backend
    if (data.msg && data.msg.toLowerCase().includes('atualizada')) {
      successMsg.value = t('movieDetails.watchedDateUpdated') || 'Data de assistido atualizada com sucesso!'
    } else {
      successMsg.value = t('movieDetails.markAsWatchedSuccess') || 'Filme adicionado com sucesso!'
    }
  } catch (e) {
    errorMsg.value = e.message
  }
  setTimeout(() => {
    successMsg.value = ''
    errorMsg.value = ''
  }, 4000)
}
</script>

<style scoped>
.adicionar-lista {
  background: rgba(30,30,30,0.95);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
  max-width: 350px;
}
</style>
