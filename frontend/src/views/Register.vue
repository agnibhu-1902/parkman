<script setup>
    import { ref } from 'vue'
    import { useRouter } from 'vue-router'
    import axios from '../config/api'

    const email = ref('')
    const name = ref('')
    const password = ref('')
    const address = ref('')
    const pincode = ref('')
    const phone = ref('')
    const registrationFailMessage = ref('')

    const router = useRouter()

    async function handleRegister() {
        try {
            const response = await axios.post('/api/register', {
                email: email.value,
                name: name.value,
                password: password.value,
                phone: phone.value,
                address: address.value,
                pincode: String(pincode.value)
            })

            if (response.status == 201 && response.data.success) {
                registrationFailMessage.value = ''
                router.push('/login')
            } else registrationFailMessage.value = response.data.message || 'Registration failed'
        } catch (error) {
            registrationFailMessage.value = error.response?.data?.message || 'Unexpected error while registering'
        }
    }
</script>

<template>
    <div class="d-flex justify-content-center align-items-center vh-100 bg-light">
        <div class="card shadow-sm p-4" style="min-width: 400px;">
            <h4 class="mb-4 text-center">Register</h4>
            <div v-if="registrationFailMessage" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill"></i>
                {{ registrationFailMessage }}
            </div>
            <form @submit.prevent="handleRegister">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input v-model="email" type="email" id="email" class="form-control" required />
                </div>

                <div class="mb-3">
                    <label for="name" class="form-label">Full Name</label>
                    <input v-model="name" type="text" id="name" class="form-control" required />
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input v-model="password" type="password" id="password" class="form-control" required />
                </div>

                <div class="mb-3">
                    <label for="phone" class="form-label">Phone Number</label>
                    <input v-model="phone" type="tel" id="phone" class="form-control" placeholder="(+91)" required />
                </div>

                <div class="mb-3">
                    <label for="address" class="form-label">Address</label>
                    <textarea v-model="address" id="address" class="form-control" rows="2"></textarea>
                </div>

                <div class="mb-3">
                    <label for="pincode" class="form-label">Pincode</label>
                    <input v-model="pincode" type="number" id="pincode" class="form-control" min="100000" max="999999" />
                </div>

                <button type="submit" class="btn btn-primary w-100 mt-3">Register</button>
            </form>
            <div class="text-center mt-3">
                Already a user? <RouterLink to="/login">Login here</RouterLink>
            </div>
        </div>
    </div>
</template>