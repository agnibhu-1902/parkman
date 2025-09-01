<script setup>
    import { ref } from 'vue'
    import { useRouter } from 'vue-router'
    import axios from '../config/api'

    const email = ref('')
    const password = ref('')
    const router = useRouter()
    const loginFailMessage = ref('')

    async function handleLogin() {
        try {
            const response = await axios.post('/api/login', {
                email: email.value,
                password: password.value
            })

            if (response.status == 200 && response.data.success) {
                loginFailMessage.value = ''
                router.push('/')
            } else loginFailMessage.value = response.data.message || 'Login failed'
        } catch (error) {
            loginFailMessage.value = error.response?.data?.message || 'Unexpected error while logging in'
        }
    }
</script>

<template>
    <div class="d-flex justify-content-center align-items-center vh-100 bg-light">
        <div class="card shadow-sm p-4" style="min-width: 400px;">
            <h4 class="mb-4 text-center">Login</h4>
            <div v-if="loginFailMessage" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill"></i>
                {{ loginFailMessage }}
            </div>
            <form @submit.prevent="handleLogin">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input v-model="email" type="email" id="email" class="form-control" required />
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input v-model="password" type="password" id="password" class="form-control" required />
                </div>

                <button type="submit" class="btn btn-primary w-100 mt-3">Login</button>
            </form>
            <div class="text-center mt-3">
                New user? <RouterLink to="/register">Create account</RouterLink>
            </div>
        </div>
    </div>
</template>