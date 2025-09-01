<script setup>
import { ref } from "vue";
import BaseModal from "./BaseModal.vue";
import axios from "../config/api";
const props = defineProps({
  spot: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["refresh"]);

const reservation = ref({});
const showInfoModal = ref(false);
const showDeleteModal = ref(false);
const deleteFailMessage = ref("");
const markFailMessage = ref("");

async function handleAutoFillUserInfo() {
  try {
    const response = await axios.get(
      `/api/reservations/${props.spot.id}/active`
    );

    if (response.status == 200 && response.data.success)
      reservation.value = response.data.reservation;
    else reservation.value = {};
  } catch (error) {
    reservation.value = {};
  }
}

async function handleDeleteSpot() {
  try {
    const response = await axios.delete(`/api/parking-spots/${props.spot.id}`);

    if (response.status == 200 && response.data.success) {
      showInfoModal.value = false;
      showDeleteModal.value = false;
      deleteFailMessage.value = "";
      emit("refresh");
    } else
      deleteFailMessage.value =
        response.data.message || "Failed to delete parking spot";
  } catch (error) {
    deleteFailMessage.value =
      error.response?.data?.message ||
      "Unexpected error while deleting parking spot";
  }
}

async function handleMarkSpot() {
  try {
    const response = await axios.patch(`/api/parking-spots/${props.spot.id}`);

    if (response.status == 200 && response.data.success) {
      showInfoModal.value = false;
      markFailMessage.value = '';
      emit('refresh');
    } else markFailMessage.value = response.data.message;
  } catch (error) {
    markFailMessage.value = error.response?.data?.message || 'Unexpected error while marking parking spot';
  }
}
</script>

<template>
  <button
    @click="
      handleAutoFillUserInfo();
      showInfoModal = true;
    "
    :title="`Spot ${spot.id}`"
    :class="['spot', spot.status]"
  >
    {{ spot.status === "occupied" ? "O" : spot.status === "available" ? "A" : "U" }}
  </button>

  <BaseModal
    :show="showInfoModal"
    title="Parking Spot Information"
    @close="showInfoModal = false; markFailMessage = ''"
  >
    <template #body>
      <div v-if="markFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ markFailMessage }}
      </div>
      <dl class="row text-start">
        <dt class="col-sm-5">Spot ID</dt>
        <dd class="col-sm-7">{{ spot.id }}</dd>

        <dt class="col-sm-5">Lot ID</dt>
        <dd class="col-sm-7">{{ spot.lot_id }}</dd>

        <dt class="col-sm-5">Status</dt>
        <dd class="col-sm-7">
          {{ spot.status.charAt(0).toUpperCase() + spot.status.slice(1) }}
        </dd>

        <template v-if="Object.keys(reservation).length !== 0">
          <dt class="col-sm-5">Customer ID</dt>
          <dd class="col-sm-7">{{ reservation.user_id }}</dd>

          <dt class="col-sm-5">Vehicle Number</dt>
          <dd class="col-sm-7">{{ reservation.vehicle_number }}</dd>

          <dt class="col-sm-5">Booking Timestamp</dt>
          <dd class="col-sm-7">{{ reservation.parking_timestamp }}</dd>

          <dt class="col-sm-5">Parking Cost</dt>
          <dd class="col-sm-7">₹{{ reservation.parking_cost }}</dd>
        </template>
      </dl>
    </template>
    <template #footer>
      <button class="btn btn-outline-secondary" @click="showInfoModal = false; markFailMessage = ''">
        Close
      </button>
      <button @click="handleMarkSpot" v-if="spot.status == 'available'" class="btn btn-warning">Mark Unavailable</button>
      <button @click="handleMarkSpot" v-if="spot.status == 'unavailable'" class="btn btn-success">Mark Available</button>
      <button
        v-if="spot.status != 'occupied'"
        class="btn btn-danger"
        @click="showDeleteModal = true; showInfoModal = false"
      >
        Delete Spot
      </button>
    </template>
  </BaseModal>

  <BaseModal
    :show="showDeleteModal"
    title="Delete Parking Spot"
    @close="showDeleteModal = false; deleteFailMessage = ''; showInfoModal = true"
    @submit="handleDeleteSpot"
  >
    <template #body>
      <div v-if="deleteFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ deleteFailMessage }}
      </div>
      <p>Are you sure you want to delete parking spot {{ spot.id }}?</p>
    </template>
    <template #footer>
      <button
        class="btn btn-outline-secondary"
        @click="showDeleteModal = false; deleteFailMessage = ''; showInfoModal = true"
      >
        Cancel
      </button>
      <button type="submit" class="btn btn-danger">Delete Spot</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.spot {
  padding: 10px 0;
  border-radius: 6px;
  font-weight: bold;
  border: 2px solid #0d6efd;
  width: 100%;
}

.available {
  background-color: #c1f7c3;
  color: #008000;
}

.available:hover {
  background-color: #028f02;
  color: white;
  transition: 0.5s ease;
}

.occupied {
  background-color: #ffc2c2;
  color: #c0392b;
}

.occupied:hover {
  background-color: #d83927;
  color: white;
  transition: 0.5s ease;
}

.unavailable {
  background-color: #f4f493;
  color: #70700b;
}

.unavailable:hover {
  background-color: #8a8a30;
  color: white;
  transition: 0.5s ease;
}
</style>
