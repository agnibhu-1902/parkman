<script setup>
import { ref, reactive, watch, onMounted } from "vue";
import { toast } from "vue3-toastify";
import axios from "../config/api";
import BaseModal from "./BaseModal.vue";

const isLocation = ref(true);
const location = ref("");
const pincode = ref("");
const parkingLots = ref([]);
const showModal = ref(false);
const bookFailMessage = ref("");
const form = reactive({
  spotID: 0,
  lotID: 0,
  userID: 0,
  vehicleNo: "",
});

const emit = defineEmits(["refresh"]);

watch([location, pincode], ([newLocation, newPincode]) => {
  if (!newLocation && !newPincode) handleSearchLots();
});

onMounted(() => handleSearchLots());

async function handleSearchLots() {
  try {
    const response = await axios.get(
      `/api/parking-lots/search?location=${location.value}&pincode=${pincode.value}`
    );

    if (response.status == 200 && response.data.success)
      parkingLots.value = response.data.lots;
    else parkingLots.value = [];
  } catch (error) {
    parkingLots.value = [];
  }
}

function handleSelectedOption(event) {
  const selected = event.target.value;
  if (selected === "location") pincode.value = "";
  else location.value = "";
  isLocation.value = selected === "location";
}

async function handleAutofill(id) {
  let response = await axios.get("/api/check-auth");
  form.userID = response.data.user.id;
  form.lotID = id;
  response = await axios.get(`/api/parking-lots/${form.lotID}/available-spot`);
  if (response.status == 200 && response.data.success)
    form.spotID = response.data.spot_id;
  else {
    bookFailMessage.value =
      response.data.message || "Failed to find an available spot";
    form.spotID = "";
  }
}

async function handleBookSpot() {
  try {
    const response = await axios.post("/api/reservations/", {
      spotID: form.spotID,
      lotID: form.lotID,
      userID: form.userID,
      vehicleNo: form.vehicleNo.toUpperCase(),
    });

    if (response.status == 201 && response.data.success) {
      showModal.value = false;
      bookFailMessage.value = "";
      emit("refresh");
      toast.success(response.data.message);
    } else
      bookFailMessage.value = response.data.message || "Failed to book spot";
  } catch (error) {
    bookFailMessage.value =
      error.response?.data?.message || "Unexpected error while booking spot";
  }
}
</script>

<template>
  <div class="container p-3" style="height: 60%">
    <div
      class="mb-4 justify-content-center align-items-center d-flex gap-5 small-vertical"
    >
      <span style="font-size: 1.5em"> Search Parking Lots </span>
      <div class="row">
        <div class="col-auto pe-0">
          <select
            class="form-select no-outline"
            @change="handleSelectedOption($event)"
            style="border-top-right-radius: 0; border-bottom-right-radius: 0"
          >
            <option value="location">Location</option>
            <option value="pincode">Pincode</option>
          </select>
        </div>
        <div class="col ps-0">
          <input
            v-if="isLocation"
            v-model="location"
            type="search"
            class="form-control d-inline no-outline"
            placeholder="Type here to search"
            style="
              border-top-left-radius: 0;
              border-bottom-left-radius: 0;
              max-width: 100%;
            "
            required
            @input="handleSearchLots"
          />
          <input
            v-if="!isLocation"
            v-model="pincode"
            type="search"
            class="form-control d-inline no-outline"
            placeholder="Type here to search"
            pattern="\d{6}"
            maxlength="6"
            style="
              border-top-left-radius: 0;
              border-bottom-left-radius: 0;
              max-width: 100%;
            "
            required
            @input="handleSearchLots"
          />
        </div>
      </div>
    </div>
    <div v-if="parkingLots.length">
      <h2 class="text-center mb-4">List of Parking Lots</h2>
      <div class="overflow-auto rounded-2" style="max-height: 15em">
        <table class="table">
          <thead class="table-light sticky-header">
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Location</th>
              <th scope="col">Address</th>
              <th scope="col" class="hide-small">Pincode</th>
              <th scope="col" class="hide-small">Availability</th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lot in parkingLots" :key="lot.id" class="align-middle">
              <td>{{ lot.id }}</td>
              <td>{{ lot.prime_location_name }}</td>
              <td>{{ lot.address }}</td>
              <td class="hide-small">{{ lot.pincode }}</td>
              <td class="hide-small">{{ lot.number_of_spots }}</td>
              <td>
                <button
                  class="btn btn-outline-success"
                  @click="
                    showModal = true;
                    handleAutofill(lot.id);
                  "
                >
                  Book
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div
      v-if="(location || pincode) && !parkingLots.length"
      class="text-center w-100 overflow-hidden"
      style="height: 85%"
    >
      <h2 class="mb-4">List of Parking Lots</h2>
      <img
        src="/images/not_found.png"
        alt="No data found"
        style="width: 200px; height: 150px"
      />
      <p class="fs-3 text-muted">No data found</p>
    </div>
  </div>
  <BaseModal
    :show="showModal"
    title="Book Parking Spot"
    @close="
      showModal = false;
      bookFailMessage = '';
    "
    @submit="handleBookSpot"
  >
    <template #body>
      <div v-if="bookFailMessage" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ bookFailMessage }}
      </div>
      <div class="mb-3">
        <label for="spotID" class="form-label">Spot ID</label>
        <input
          v-model="form.spotID"
          type="number"
          class="form-control bg-light no-outline"
          id="spotID"
          style="cursor: not-allowed"
          readonly
        />
      </div>
      <div class="mb-3">
        <label for="lotID" class="form-label">Lot ID</label>
        <input
          v-model="form.lotID"
          type="number"
          class="form-control bg-light no-outline"
          id="lotID"
          style="cursor: not-allowed"
          readonly
        />
      </div>
      <div class="mb-3">
        <label for="userID" class="form-label">User ID</label>
        <input
          v-model="form.userID"
          type="number"
          class="form-control bg-light no-outline"
          id="userID"
          style="cursor: not-allowed"
          readonly
        />
      </div>
      <div class="mb-3">
        <label for="vehicleNo" class="form-label">Vehicle Number</label>
        <input
          v-model="form.vehicleNo"
          type="text"
          class="form-control text-uppercase"
          id="vehicleNo"
          pattern="^[A-Za-z]{2}[0-9]{2}[A-Za-z]{1,3}[0-9]{4}"
          required
        />
      </div>
    </template>
    <template #footer>
      <button
        class="btn btn-outline-secondary"
        @click="
          showModal = false;
          bookFailMessage = '';
        "
      >
        Cancel
      </button>
      <button type="submit" class="btn btn-success">Book Spot</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.no-outline:focus {
  outline: none !important;
  box-shadow: none !important;
}

.sticky-header {
  position: sticky;
  top: 0;
  z-index: 2;
}

@media (max-width: 768px) {
  .small-vertical {
    flex-direction: column;
  }
}

@media (max-width: 572px) {
  .hide-small {
    display: none;
  }
}
</style>
