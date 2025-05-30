<script setup>
import { RouterView, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const router = useRouter()
const { locale } = useI18n()

const closeNavbarIfNeeded = () => {
  const collapsibleNavbarElement = document.getElementById('navbarNav');
  if (!collapsibleNavbarElement) {
    // console.error('#navbarNav element not found');
    return;
  }

  const navbarToggler = document.querySelector('.navbar-toggler');
  if (!navbarToggler || getComputedStyle(navbarToggler).display === 'none') {
    // Not in mobile view where toggler is active, or toggler not found
    return;
  }

  if (collapsibleNavbarElement.classList.contains('show')) {
    let bsCollapseInstance = null;
    if (window.bootstrap && typeof window.bootstrap.Collapse === 'function') {
      bsCollapseInstance = window.bootstrap.Collapse.getInstance(collapsibleNavbarElement);
    }

    if (bsCollapseInstance) {
      bsCollapseInstance.hide();
    } else {
      // Fallback if Bootstrap JS API isn't available or instance not found
      // console.warn('Bootstrap Collapse instance not found for #navbarNav. Falling back to toggler click.');
      navbarToggler.click();
    }
  }
};

const handleLogout = () => {
  authStore.logout()
  router.push('/') 
  closeNavbarIfNeeded(); 
}

// Screen size logging utility
const screenWidth = ref(0);
const screenHeight = ref(0);

const logScreenSize = () => {
  if (typeof window !== 'undefined') {
    screenWidth.value = window.innerWidth;
    screenHeight.value = window.innerHeight;
    console.log(`Current screen dimensions: Width = ${screenWidth.value}px, Height = ${screenHeight.value}px`);
  }
};

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', logScreenSize);
    logScreenSize(); // Log initial size
  }
});

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', logScreenSize);
  }
});

function toggleLanguage() {
  locale.value = locale.value === 'en' ? 'pt' : 'en'
}
</script>

<template>
  <div class="app-wrapper">
    <header>
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container-fluid px-2 px-sm-3">
          <RouterLink to="/" class="navbar-brand py-1 py-md-2" @click="closeNavbarIfNeeded">
            <span class="brand-meus">Meus</span><span class="brand-filmes">Filmes</span>
          </RouterLink>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <RouterLink to="/" class="nav-link" active-class="active" @click="closeNavbarIfNeeded">{{ $t('nav.home') }}</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink to="/buscar" class="nav-link" active-class="active" @click="closeNavbarIfNeeded">{{ $t('nav.search') }}</RouterLink>
              </li>
              <template v-if="authStore.isAuthenticated">
                <li class="nav-item">
                  <RouterLink to="/listas" class="nav-link" active-class="active" @click="closeNavbarIfNeeded">{{ $t('nav.myLists') }}</RouterLink>
                </li>
                <li class="nav-item">
                  <RouterLink to="/assistidos" class="nav-link" active-class="active" @click="closeNavbarIfNeeded">{{ $t('nav.watched') }}</RouterLink>
                </li>
              </template>
            </ul>
            <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-center">
              <li class="nav-item">
                <button class="btn btn-outline-light d-flex align-items-center gap-1" @click="toggleLanguage" style="font-weight: bold;">
                  <i class="bi bi-globe2"></i>
                  <span style="font-size: 1rem; letter-spacing: 1px;">{{ locale.toUpperCase().slice(0,2) }}</span>
                </button>
              </li>
              <template v-if="authStore.isAuthenticated">
                <li class="nav-item">
                  <span class="nav-link text-warning">{{ authStore.userName }}</span>
                </li>
                <li class="nav-item">
                  <button @click="handleLogout" class="btn btn-outline-danger btn-sm">{{ $t('nav.logout') }}</button>
                </li>
              </template>
              <template v-else>
                <li class="nav-item">
                  <RouterLink to="/login" class="nav-link" active-class="active" @click="closeNavbarIfNeeded">{{ $t('nav.login') }}</RouterLink>
                </li>
                <li class="nav-item">
                  <RouterLink to="/registrar" class="nav-link" active-class="active" @click="closeNavbarIfNeeded">{{ $t('nav.register') }}</RouterLink>
                </li>
              </template>
            </ul>
          </div>
        </div>
      </nav>
    </header>

    <main class="container-fluid container-md mt-4 mt-md-5 pt-4 pt-md-5 main-content px-2 px-sm-3 px-md-4"> <!-- Adjusting spacing for mobile -->
      <RouterView />
    </main>

    <footer class="bg-dark text-light text-center py-2 py-md-3 mt-auto">
      <div class="container">
        <p class="mb-1">&copy; {{ new Date().getFullYear() }} MeusFilmes. {{ $t('footer.rights') }}</p>
        <p class="mb-0">{{ $t('footer.madeWith') }} <span class="text-danger">&hearts;</span> {{ $t('footer.andVue') }}</p>
      </div>
    </footer>
  </div>
</template>

<style>
/* Estilos globais (não scoped) para afetar toda a aplicação */
html, 
body {
  background-color: #121212 !important; /* Cor de fundo escura, mas não preto absoluto */
  color: #f0f0f0 !important; /* Cor de texto claro para contraste */
  min-height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  height: 100% !important;
}

#app {
  background-color: #121212 !important;
  color: #f0f0f0 !important;
  min-height: 100vh !important;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #121212 !important;
}
</style>

<style scoped>
/* Keep minimal custom styles, Bootstrap handles most of it */

.navbar-brand {
  font-weight: bold;
  color: #a259ff !important; /* Custom brand color */
}

.navbar-brand:hover {
  color: #b87eff !important;
}

/* Styling for active and non-active nav links */
.nav-link.active {
  color: #ffffff !important; 
  font-weight: bold;
}

.nav-link:not(.active) {
  color: #adb5bd !important; /* Softer color for non-active links */
}

.nav-link:hover:not(.active) {
  color: #e9ecef !important; /* Lighter on hover for non-active */
}

.main-content {
  flex: 1; /* Allows main content to expand and push footer down */
  background-color: #101010 !important;
  color: #f0f0f0 !important;
  padding-bottom: 2rem; /* Ensure space above footer */
}

.heart {
  color: #a259ff; /* Custom heart color, Bootstrap text-danger is used in template for consistency */
}

.brand-meus {
  color: #2196f3 !important; /* Bootstrap primary blue */
  font-weight: bold;
}

.brand-filmes {
  color: #ff1744 !important; /* Bootstrap danger red */
  font-weight: bold;
}

/* Removed all previous media queries as Bootstrap handles responsiveness */
</style>
