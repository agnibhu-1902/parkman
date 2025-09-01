<script setup>
import { ref, onMounted, reactive } from "vue";
import axios from "../config/api";
import { useSearchStore } from "../stores/useSearchStore";
import { useRouter, useRoute } from "vue-router";
import { toast } from "vue3-toastify";
import BaseModal from "./BaseModal.vue";

const user = ref({});
const isAdmin = ref(false);
const router = useRouter();
const route = useRoute();
const showModal = ref(false);
const editFailMessage = ref("");
const showConfirmPassword = ref(false);
const showChangePassword = ref(false);
const form = reactive({
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
  address: "",
  pincode: "",
});
const selectedOption = reactive({
  parkingLotPincode: "",
  parkingLotName: "",
  userFullName: "",
  userEmail: "",
  optionValue: "parkingLotName",
});

function clearSelectedOption() {
  selectedOption.parkingLotPincode = "";
  selectedOption.parkingLotName = "";
  selectedOption.userFullName = "";
  selectedOption.userEmail = "";
  handleSearchQuery();
}

const searchStore = useSearchStore();
const handleSearchQuery = () => {
  searchStore.setSearchQuery(
    `${selectedOption.optionValue}=${
      selectedOption[selectedOption.optionValue]
    }`
  );
};

function isActive(path) {
  return route.path === path;
}

async function setAuth() {
  const response = await axios.get("/api/check-auth");
  user.value = response.data.user;
  isAdmin.value = Boolean(response.data.user.is_admin);
  return response;
}

onMounted(async () => {
  try {
    const response = await setAuth();
    form.name = response.data.user.name;
    form.email = response.data.user.email;
    form.address = response.data.user.address;
    form.pincode = response.data.user.pincode;
  } catch (err) {
    console.error("User not logged in");
  }
});

async function logout() {
  await axios.post("/api/logout", {});
  router.push("/login");
}

async function handleEditProfile() {
  try {
    const response = await axios.put(`/api/users/${user.value.id}`, {
      name: form.name,
      email: form.email,
      password: form.password,
      confirmPassword: form.confirmPassword,
      address: form.address,
      pincode: form.pincode,
    });

    if (response.status == 200 && response.data.success) {
      showModal.value = false;
      showChangePassword.value = false;
      editFailMessage.value = "";
      toast.success(response.data.message);
    } else
      editFailMessage.value = response.data.message || "Failed to edit profile";
  } catch (error) {
    editFailMessage.value =
      error.response?.data?.message || "Unexpected error while editing profile";
  }
}

function handleSelectedOption(event) {
  const selected = event.target.value;
  selectedOption.optionValue = selected;
}

async function exportCSV() {
  try {
    const response = await axios.post("/api/exports/csv", {});

    if (response.status == 201 && response.data.success)
      toast.success("Export started! Check your inbox or download page.");
    else toast.error(response.data.message);
  } catch (error) {
    console.error("Fail");
    toast.error("Unexpected error while exporting! Try again later.");
  }
}

function openDocs() {
  const url = `${import.meta.env.VITE_API_BASE_URL}/docs`;
  window.open(url, "_blank");
}
</script>

<template>
  <nav class="navbar navbar-expand-lg bg-body-tertiary fixed-top">
    <div class="container-fluid">
      <RouterLink :to="isAdmin ? '/admin/' : '/'" class="navbar-brand cedarville-cursive"
        >ParkMan</RouterLink
      >
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li @click="clearSelectedOption" class="nav-item">
            <RouterLink
              :to="isAdmin ? '/admin/' : '/'"
              :class="[
                'nav-link',
                (isActive('/') || isActive('/admin/')) && 'active',
              ]"
              :aria-current="(isActive('/') || isActive('/admin/')) && 'page'"
              >Home</RouterLink
            >
          </li>
          <li v-if="isAdmin" @click="clearSelectedOption" class="nav-item">
            <RouterLink
              to="/admin/users"
              :class="['nav-link', isActive('/admin/users') && 'active']"
              :aria-current="isActive('/admin/users') && 'page'"
              >Users</RouterLink
            >
          </li>
          <li @click="clearSelectedOption" class="nav-item">
            <RouterLink
              :to="isAdmin ? '/admin/summary' : '/summary'"
              :class="[
                'nav-link',
                (isActive('/admin/summary') || isActive('/summary')) &&
                  'active',
              ]"
              :aria-current="
                (isActive('/admin/summary') || isActive('/summary')) && 'page'
              "
              >Summary</RouterLink
            >
          </li>
          <li class="nav-item dropdown">
            <a
              class="nav-link dropdown-toggle d-flex align-items-center gap-1"
              href="#"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <img src="/images/default_avatar.png" alt="User Profile" class="rounded-circle" style="width: 25px; height: 25px; object-fit: cover;" />
              {{ user.name }}<span
                v-if="user.is_admin"
                class="badge rounded-pill text-bg-warning"
                >admin</span
              >
            </a>
            <ul class="dropdown-menu">
              <li>
                <a @click="showModal = true" class="dropdown-item" href="#"
                  ><i class="bi bi-person-fill"></i>&nbsp;Edit Profile</a
                >
              </li>
              <li v-if="!isAdmin">
                <a @click="exportCSV" class="dropdown-item" href="#"
                  ><i class="bi bi-file-earmark-arrow-up-fill"></i>&nbsp;Export
                  as CSV</a
                >
              </li>
              <li>
                <a @click="openDocs" class="dropdown-item" href="#"
                  ><i class="bi bi-eye-fill"></i>&nbsp;View API Docs</a
                >
              </li>
              <li>
                <a @click="logout" class="dropdown-item" href="#"
                  ><i class="bi bi-door-closed-fill"></i>&nbsp;Logout</a
                >
              </li>
            </ul>
          </li>
        </ul>
        <form v-if="isAdmin" class="d-flex" role="search">
          <div class="col-auto pe-0">
            <select
              class="form-select no-outline"
              @change="handleSelectedOption($event)"
              style="border-top-right-radius: 0; border-bottom-right-radius: 0"
            >
              <option value="parkingLotName" selected>Parking Lot Name</option>
              <option value="parkingLotPincode">Parking Lot Pincode</option>
              <option value="userFullName">User Full Name</option>
              <option value="userEmail">User Email</option>
            </select>
          </div>
          <div class="col ps-0">
            <input
              v-if="selectedOption.optionValue === 'parkingLotName'"
              v-model="selectedOption.parkingLotName"
              type="search"
              class="form-control d-inline w-auto no-outline"
              placeholder="Type here to search"
              style="border-top-left-radius: 0; border-bottom-left-radius: 0"
              required
              @input="handleSearchQuery"
            />
            <input
              v-if="selectedOption.optionValue === 'parkingLotPincode'"
              v-model="selectedOption.parkingLotPincode"
              type="search"
              class="form-control d-inline w-auto no-outline"
              placeholder="Type here to search"
              style="border-top-left-radius: 0; border-bottom-left-radius: 0"
              required
              @input="handleSearchQuery"
            />
            <input
              v-if="selectedOption.optionValue === 'userFullName'"
              v-model="selectedOption.userFullName"
              type="search"
              class="form-control d-inline w-auto no-outline"
              placeholder="Type here to search"
              style="border-top-left-radius: 0; border-bottom-left-radius: 0"
              required
              @input="handleSearchQuery"
            />
            <input
              v-if="selectedOption.optionValue === 'userEmail'"
              v-model="selectedOption.userEmail"
              type="search"
              class="form-control d-inline w-auto no-outline"
              placeholder="Type here to search"
              style="border-top-left-radius: 0; border-bottom-left-radius: 0"
              required
              @input="handleSearchQuery"
            />
          </div>
        </form>
      </div>
    </div>
  </nav>
  <BaseModal
    :show="showModal"
    title="Edit Profile"
    @close="
      showModal = false;
      editFailMessage = '';
      showChangePassword = false;
    "
    @submit="handleEditProfile"
  >
    <template #body>
      <div v-if="editFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ editFailMessage }}
      </div>
      <div class="mb-3">
        <label for="name" class="form-label">Full Name</label>
        <input v-model="form.name" type="text" class="form-control" id="name" />
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input
          v-model="form.email"
          type="email"
          class="form-control"
          id="email"
        />
      </div>
      <div class="mb-3">
        <label for="address" class="form-label">Address</label>
        <textarea
          v-model="form.address"
          id="address"
          class="form-control"
        ></textarea>
      </div>
      <div class="mb-3">
        <label for="pincode" class="form-label">Pincode</label>
        <input
          v-model="form.pincode"
          type="number"
          class="form-control"
          id="pincode"
          min="100000"
          max="999999"
        />
      </div>
      <a
        @click="showChangePassword = true"
        v-if="!showChangePassword"
        href="#"
        class="link-secondary"
        >Change Password?</a
      >
      <div v-if="showChangePassword" class="mb-3">
        <label for="password" class="form-label">New Password</label>
        <input
          @beforeinput="showConfirmPassword = false"
          @input="showConfirmPassword = true"
          v-model="form.password"
          type="password"
          class="form-control"
          id="password"
        />
      </div>
      <div v-if="showChangePassword && showConfirmPassword" class="mb-3">
        <label for="confirmPassword" class="form-label">Confirm Password</label>
        <input
          v-model="form.confirmPassword"
          type="password"
          class="form-control"
          id="confirmPassword"
        />
      </div>
    </template>
    <template #footer>
      <button
        class="btn btn-outline-secondary"
        @click="
          showModal = false;
          showChangePassword = false;
          editFailMessage = '';
        "
      >
        Cancel
      </button>
      <button type="submit" class="btn btn-primary">Edit Profile</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.no-outline:focus {
  outline: none !important;
  box-shadow: none !important;
}

.cedarville-cursive {
  font-family: "Cedarville Cursive", cursive;
  font-weight: 400;
  font-style: bold;
}

</style>
