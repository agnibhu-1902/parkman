<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { toast } from "vue3-toastify";
import BaseModal from "./BaseModal.vue";
import ParkingSpotButton from "./ParkingSpotButton.vue";
import axios from "../config/api";

const props = defineProps({
  lot: {
    type: Object,
    required: true,
  },
});

const showEditModal = ref(false);
const showDeleteModal = ref(false);
const showInfoModal = ref(false);
const id = ref(0);
const primeLocationName = ref("");
const address = ref("");
const pincode = ref("");
const price = ref(0);
const maxSpots = ref(0);
const parkingSpots = ref([]);
const isHovered = ref(false);
const deleteFailMessage = ref("");
const editFailMessage = ref("");
let intervalID = null;

const emit = defineEmits(["refresh"]);

async function fetchParkingSpots() {
  const response = await axios.get(`/api/parking-lots/${props.lot.id}/spots`);
  if (response.status == 200 && response.data.success)
    parkingSpots.value = response.data.spots;
}

onMounted(async () => {
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach((el) => new bootstrap.Tooltip(el));

  id.value = props.lot.id;
  primeLocationName.value = props.lot.prime_location_name;
  address.value = props.lot.address;
  pincode.value = props.lot.pincode;
  price.value = props.lot.price;
  maxSpots.value = props.lot.number_of_spots;

  await fetchParkingSpots();
  intervalID = setInterval(() => fetchParkingSpots(), 5000);
});

onUnmounted(() => {
  if (intervalID) clearInterval(intervalID);
});

async function handleEditLot() {
  try {
    const response = await axios.put(`/api/parking-lots/${id.value}`, {
      primeLocationName: primeLocationName.value,
      address: address.value,
      pincode: String(pincode.value),
      price: price.value,
      maxSpots: maxSpots.value,
    });

    if (response.status == 200 && response.data.success) {
      editFailMessage.value = "";
      showEditModal.value = false;
      emit("refresh");
      await fetchParkingSpots();
      toast.success(response.data.message);
    } else editFailMessage.value = response.data.message || "Edit failed";
  } catch (error) {
    editFailMessage.value =
      error.response?.data?.message || "Unexpected error while editing";
  }
}

async function handleDeleteLot() {
  try {
    const response = await axios.delete(`/api/parking-lots/${id.value}`);

    if (response.status == 200 && response.data.success) {
      showDeleteModal.value = false;
      deleteFailMessage.value = "";
      emit("refresh");
      toast.success(response.data.message);
    } else deleteFailMessage.value = response.data.message || "Deletion failed";
  } catch (error) {
    deleteFailMessage.value =
      error.response?.data?.message || "Unexpected error while deleting";
  }
}
</script>

<template>
  <div class="card parking-card text-center p-3 shadow-sm h-100">
    <!-- Title and Actions -->
    <h5 class="card-title mb-1">
      {{ lot.prime_location_name }}&nbsp;<i
        data-bs-toggle="tooltip"
        data-bs-placement="bottom"
        data-bs-title="Show more information"
        @click="showInfoModal = true"
        @mouseenter="isHovered = true"
        @mouseleave="isHovered = false"
        :class="[
          'bi',
          'info-btn',
          isHovered ? 'bi-info-circle-fill' : 'bi-info-circle',
          'small',
        ]"
      ></i>
    </h5>
    <div class="fw-bold small">
      <a
        href="#"
        class="me-2 text-decoration-none text-warning"
        @click="showEditModal = true"
      >
        <i class="bi bi-pen-fill"></i>
        Edit</a
      >
      <a
        href="#"
        class="ms-2 text-decoration-none text-danger"
        @click="showDeleteModal = true"
      >
        <i class="bi bi-trash3-fill"></i>
        Delete</a
      >
    </div>

    <!-- Occupied Status -->
    <div class="text-secondary fw-bold mt-2 mb-3">
      Occupied:
      {{ parkingSpots.filter((spot) => spot.status === "occupied").length }}/{{
        parkingSpots.length
      }}
    </div>

    <!-- Grid of Spots -->
    <div class="parking-grid overflow-auto" style="max-height: 150px">
      <div v-for="(spot, index) in parkingSpots" :key="index">
        <ParkingSpotButton @refresh="fetchParkingSpots" :spot />
      </div>
    </div>
  </div>
  <BaseModal
    :show="showEditModal"
    title="Edit Parking Lot"
    @close="
      showEditModal = false;
      editFailMessage = '';
    "
    @submit="handleEditLot"
  >
    <template #body>
      <div v-if="editFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ editFailMessage }}
      </div>
      <div class="mb-3">
        <label for="primeLocationName" class="form-label"
          >Prime Location Name</label
        >
        <input
          v-model="primeLocationName"
          type="text"
          class="form-control"
          id="primeLocationName"
        />
      </div>
      <div class="mb-3">
        <label for="address" class="form-label">Address</label>
        <textarea
          v-model="address"
          id="address"
          class="form-control"
        ></textarea>
      </div>
      <div class="mb-3">
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
      <div class="mb-3">
        <label for="price" class="form-label">Price Per Hour (in ₹)</label>
        <input
          v-model="price"
          type="number"
          class="form-control"
          id="price"
          min="0"
        />
      </div>
      <div class="mb-3">
        <label for="maxSpots" class="form-label">Maximum Spots</label>
        <input
          v-model="maxSpots"
          type="number"
          class="form-control"
          id="maxSpots"
          min="0"
        />
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
      <button type="submit" class="btn btn-primary">Edit Lot</button>
    </template>
  </BaseModal>

  <BaseModal
    :show="showDeleteModal"
    title="Delete Parking Lot"
    @close="
      showDeleteModal = false;
      deleteFailMessage = '';
    "
    @submit="handleDeleteLot"
  >
    <template #body>
      <div v-if="deleteFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ deleteFailMessage }}
      </div>
      <p>Are you sure you want to delete this parking lot?</p>
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
      <button type="submit" class="btn btn-danger">Delete Lot</button>
    </template>
  </BaseModal>

  <BaseModal
    :show="showInfoModal"
    title="Parking Lot Information"
    @close="showInfoModal = false"
  >
    <template #body>
      <dl class="row">
        <dt class="col-sm-5">Prime Location Name</dt>
        <dd class="col-sm-7">{{ lot.prime_location_name }}</dd>

        <dt class="col-sm-5">Address</dt>
        <dd class="col-sm-7">{{ lot.address }}</dd>

        <dt class="col-sm-5">Pincode</dt>
        <dd class="col-sm-7">{{ lot.pincode }}</dd>

        <dt class="col-sm-5">Price Per Hour</dt>
        <dd class="col-sm-7">₹{{ lot.price }}</dd>

        <dt class="col-sm-5">Number of Spots</dt>
        <dd class="col-sm-7">{{ lot.number_of_spots }}</dd>

        <dt class="col-sm-5">Occupied</dt>
        <dd class="col-sm-7">
          {{ parkingSpots.filter((spot) => spot.status === "occupied").length }}
        </dd>

        <dt class="col-sm-5">Unavailable</dt>
        <dd class="col-sm-7">
          {{
            parkingSpots.filter((spot) => spot.status === "unavailable").length
          }}
        </dd>

        <dt class="col-sm-5">Vacant</dt>
        <dd class="col-sm-7">
          {{
            parkingSpots.filter((spot) => spot.status === "available").length
          }}
        </dd>
      </dl>
    </template>
    <template #footer>
      <button class="btn btn-outline-secondary" @click="showInfoModal = false">
        Close
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.parking-card {
  border: 2px solid #0077cc;
  border-radius: 12px;
  width: 250px;
}

.parking-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  margin-top: 10px;
}

.info-btn:hover {
  cursor: pointer;
}
</style>
