<script setup>
import { ref, onMounted, reactive } from "vue";
import { toast } from "vue3-toastify";
import axios from "../config/api";
import BaseModal from "./BaseModal.vue";

const props = defineProps({
  reservations: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["refresh"]);

const showInfoModal = ref(false);
const showReleaseModal = ref(false);
const releaseFailMessage = ref("");

const data = reactive({
  id: 0,
  spotID: 0,
  location: "",
  vehicleNo: "",
  address: "",
  parkingTimestamp: "",
  leavingTimestamp: "",
  status: "",
  price: 0.0
});

async function handleMarkSpot() {
  try {
    const response = await axios.patch("/api/reservations/", {
      id: data.id,
    });
    if (response.status == 200 && response.data.success) {
      showReleaseModal.value = false;
      releaseFailMessage.value = "";
      emit("refresh");
      toast.success(response.data.message);
    } else
      releaseFailMessage.value =
        response.data.message || "Failed to mark parking spot";
  } catch (error) {
    releaseFailMessage.value =
      error.response?.data?.message ||
      "Unexpected error while marking parking spot";
  }
}

function handleAutoFill(resID) {
  const reservation = props.reservations.filter(
    (reservation) => reservation.id == resID
  )[0];
  data.id = reservation.id;
  data.spotID = reservation.spot_id;
  data.location = reservation.location;
  data.address = reservation.address;
  data.parkingTimestamp = reservation.parking_timestamp;
  data.leavingTimestamp = reservation.leaving_timestamp;
  data.vehicleNo = reservation.vehicle_number;
  data.status = reservation.status;
  data.price = reservation.parking_cost;
}

onMounted(() => {
  emit("refresh");
});
</script>

<template>
  <div class="container p-3" style="height: 40%">
    <h2 class="text-center mb-4">Recent Parking History</h2>
    <div
      v-if="reservations.length"
      class="overflow-auto rounded-2"
      style="max-height: 70%"
    >
      <table class="table">
        <thead class="table-light sticky-header">
          <tr>
            <th scope="col">Spot ID</th>
            <th scope="col">Location</th>
            <th scope="col" class="hide-small">Vehicle Number</th>
            <th scope="col" class="hide-small">Timestamp</th>
            <th scope="col">Status</th>
            <th scope="col">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="reservation in props.reservations"
            :key="reservation.id"
            class="align-middle"
          >
            <td>{{ reservation.spot_id }}</td>
            <td>{{ reservation.location }}</td>
            <td class="hide-small">{{ reservation.vehicle_number }}</td>
            <td class="hide-small">{{ reservation.parking_timestamp }}</td>
            <td
              :class="
                reservation.status === 'active'
                  ? 'text-primary'
                  : reservation.status === 'pending'
                  ? 'text-danger'
                  : 'text-success'
              "
            >
              {{
                reservation.status === "completed"
                  ? "Parked Out"
                  : reservation.status === "pending"
                  ? "Not Parked"
                  : "Parked In"
              }}
            </td>
            <td>
              <div class="d-flex gap-2 small-vertical">
                <button
                  class="btn btn-outline-secondary"
                  @click="
                    handleAutoFill(reservation.id);
                    showInfoModal = true;
                  "
                >
                  View
                </button>
                <button
                  v-if="reservation.status === 'active'"
                  class="btn btn-outline-danger"
                  @click="
                    handleAutoFill(reservation.id);
                    showReleaseModal = true;
                  "
                >
                  Release
                </button>
                <button
                  v-if="reservation.status === 'pending'"
                  class="btn btn-outline-primary"
                  @click="
                    handleAutoFill(reservation.id);
                    handleMarkSpot();
                  "
                >
                  Park
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-if="!reservations.length"
      class="text-center w-100 h-100 overflow-hidden"
    >
      <img
        src="/images/sad_ghost.png"
        alt="No data found"
        style="width: 200px; height: 150px"
      />
      <p class="fs-3 text-muted">Nothing to show here</p>
    </div>
  </div>
  <BaseModal
    :show="showInfoModal"
    title="Spot Booking Information"
    @close="showInfoModal = false"
  >
    <template #body>
      <dl class="row px-1">
        <dt class="col-sm-5">Spot ID</dt>
        <dd class="col-sm-7">{{ data.spotID }}</dd>

        <dt class="col-sm-5">Prime Location Name</dt>
        <dd class="col-sm-7">{{ data.location }}</dd>

        <dt class="col-sm-5">Address</dt>
        <dd class="col-sm-7">{{ data.address }}</dd>

        <dt class="col-sm-5">Vehicle Number</dt>
        <dd class="col-sm-7">{{ data.vehicleNo }}</dd>

        <dt class="col-sm-5">Booking Timestamp</dt>
        <dd class="col-sm-7">{{ data.parkingTimestamp }}</dd>

        <dt class="col-sm-5" v-if="data.leavingTimestamp">Leaving Timestamp</dt>
        <dd class="col-sm-7" v-if="data.leavingTimestamp">
          {{ data.leavingTimestamp }}
        </dd>

        <dt class="col-sm-5">Status</dt>
        <dd class="col-sm-7">
          {{
            data.status === "active"
              ? "Parked In"
              : data.status === "pending"
              ? "Not Parked"
              : "Parked Out"
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

  <BaseModal
    :show="showReleaseModal"
    title="Release Parking Spot"
    @close="
      showReleaseModal = false;
      releaseFailMessage = '';
    "
    @submit="handleMarkSpot"
  >
    <template #body>
      <div v-if="releaseFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ releaseFailMessage }}
      </div>
      <p>Are you sure you want to release this parking spot?</p>
      <p>Amount to pay: <strong>₹{{ data.price }}</strong></p>
    </template>
    <template #footer>
      <button
        class="btn btn-outline-secondary"
        @click="
          showReleaseModal = false;
          releaseFailMessage = '';
        "
      >
        Cancel
      </button>
      <button type="submit" class="btn btn-danger">Release Spot</button>
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

@media (max-width: 464px) {
  .small-vertical {
    flex-direction: column;
  }
}
</style>
