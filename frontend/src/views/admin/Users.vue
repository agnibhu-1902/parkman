<script setup>
import { watch, ref, onMounted } from "vue";
import { useSearchStore } from "../../stores/useSearchStore";
import { useRouter } from "vue-router";
import { toast } from "vue3-toastify";
import axios from "../../config/api";
import BaseModal from "../../components/BaseModal.vue";

const searchStore = useSearchStore();
const router = useRouter();

const users = ref([]);
const showEditModal = ref(false);
const editFailMessage = ref("");
const showDeleteModal = ref(false);
const deleteFailMessage = ref("");
const id = ref(0);
const name = ref("");
const email = ref("");
const address = ref("");
const pincode = ref("");
const isAdmin = ref(false);

async function fetchSearchResults(query) {
  const [key, value] = query.split("=");

  if (value === "") return fetchUsers();

  if (key.slice(0, 4) !== "user") router.push("/");

  const response = await axios.get(`/api/users/admin/search?${query}`);

  if (response.status == 200 && response.data.success)
    users.value = response.data.users;
}

async function fetchUsers() {
  const response = await axios.get("/api/users/");

  if (response.status == 200 && response.data.success)
    users.value = response.data.users;
}

function fetchUser(userId) {
  const user = users.value.find((user) => user.id === userId);
  id.value = userId;
  name.value = user.name;
  address.value = user.address;
  pincode.value = user.pincode;
  isAdmin.value = user.is_admin;
}

async function handleEditUser() {
  try {
    const response = await axios.patch(`/api/users/${id.value}`, {
      name: name.value,
      email: email.value,
      address: address.value,
      pincode: pincode.value,
      isAdmin: isAdmin.value,
    });

    if (response.status == 200 && response.data.success) {
      showEditModal.value = false;
      editFailMessage.value = "";
      await fetchUsers();
      toast.success(response.data.message);
    } else editFailMessage.value = response.data.message || "Edit failed";
  } catch (error) {
    editFailMessage.value =
      error.response?.data?.message || "Unexpected error while editing";
  }
}

async function handleDeleteUser() {
  try {
    const response = await axios.delete(`/api/users/${id.value}`);

    if (response.status == 200 && response.data.success) {
      showDeleteModal.value = false;
      deleteFailMessage.value = "";
      await fetchUsers();
      toast.success(response.data.message);
    } else deleteFailMessage.value = response.data.message || "Delete failed";
  } catch (error) {
    deleteFailMessage.value =
      error.response?.data?.message || "Unexpected error while deleting";
  }
}

onMounted(async () => {
  await fetchSearchResults(searchStore.searchQuery);
});

watch(
  () => searchStore.searchQuery,
  (newQuery) => fetchSearchResults(newQuery)
);
</script>

<template>
  <div class="vh-100 container" style="padding-top: 70px">
    <h1 class="mb-4 text-center">Registered Users</h1>
    <div v-if="users.length" class="table-responsive rounded-2" style="height: 80%">
      <table class="table align-middle">
        <thead class="table-light sticky-header">
          <tr>
            <th scope="col">ID</th>
            <th scope="col">Full Name</th>
            <th scope="col">Email</th>
            <th scope="col" class="hide-small">Address</th>
            <th scope="col" class="hide-small">Pincode</th>
            <th scope="col">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>
              {{ user.name }} &nbsp;<span
                v-if="user.is_admin"
                class="badge rounded-pill text-bg-warning"
                >admin</span
              >
            </td>
            <td class="text-break">{{ user.email }}</td>
            <td class="hide-small">{{ user.address }}</td>
            <td class="hide-small">{{ user.pincode }}</td>
            <td>
              <div class="d-flex gap-2 small-vertical">
                <button
                  title="Edit user details"
                  @click="
                    fetchUser(user.id);
                    showEditModal = true;
                  "
                  class="btn btn-outline-secondary"
                >
                  <i class="bi bi-pen-fill"></i>
                </button>
                <button
                  title="Delete user"
                  @click="
                    fetchUser(user.id);
                    showDeleteModal = true;
                  "
                  class="btn btn-outline-danger"
                >
                  <i class="bi bi-trash3-fill"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
        v-if="!users.length"
        class="text-center w-100 h-100 overflow-hidden"
      >
        <img
          src="/images/not_found.png"
          alt="No data found"
          style="width: 200px; height: 150px"
        />
        <p class="fs-3 text-muted">No data found</p>
      </div>
  </div>
  <BaseModal
    :show="showEditModal"
    title="Edit User Details"
    @close="
      showEditModal = false;
      editFailMessage = '';
    "
    @submit="handleEditUser"
  >
    <template #body>
      <div v-if="editFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ editFailMessage }}
      </div>
      <div class="mb-3">
        <label for="name" class="form-label">Full Name</label>
        <input v-model="name" type="text" class="form-control" id="name" />
      </div>
      <div class="mb-3">
        <label for="address" class="form-label">Address</label>
        <textarea
          v-model="address"
          id="address"
          class="form-control"
        ></textarea>
      </div>
      <div class="mb-4">
        <label for="pincode" class="form-label">Pincode</label>
        <input
          v-model="pincode"
          type="number"
          class="form-control"
          id="pincode"
          min="100000"
          max="999999"
        />
      </div>
      <div class="form-check mb-3">
        <input
          v-model="isAdmin"
          class="form-check-input"
          type="checkbox"
          id="isAdmin"
        />
        <label class="form-check-label" for="isAdmin">
          Allow Administrator Privileges
        </label>
      </div>
    </template>
    <template #footer>
      <button
        class="btn btn-outline-secondary"
        @click="
          showEditModal = false;
          editFailMessage = '';
        "
      >
        Cancel
      </button>
      <button type="submit" class="btn btn-primary">Edit User</button>
    </template>
  </BaseModal>

  <BaseModal
    :show="showDeleteModal"
    title="Delete User"
    @close="
      showDeleteModal = false;
      deleteFailMessage = '';
    "
    @submit="handleDeleteUser"
  >
    <template #body>
      <div v-if="deleteFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ deleteFailMessage }}
      </div>
      <p>Are you sure you want to delete this user?</p>
    </template>
    <template #footer>
      <button
        class="btn btn-outline-secondary"
        @click="
          showDeleteModal = false;
          deleteFailMessage = '';
        "
      >
        Cancel
      </button>
      <button type="submit" class="btn btn-danger">Delete User</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 2;
}

@media (max-width: 768px) {
  .hide-small {
    display: none;
  }
}

@media (max-width: 578px) {
  .small-vertical {
    flex-direction: column;
  }
}
</style>
