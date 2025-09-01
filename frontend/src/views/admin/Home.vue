<script setup>
import { watch, ref, onMounted } from "vue";
import { useSearchStore } from "../../stores/useSearchStore";
import BaseModal from "../../components/BaseModal.vue";
import ParkingLotCard from "../../components/ParkingLotCard.vue";
import axios from "../../config/api";
import { useRouter } from "vue-router";
import { toast } from "vue3-toastify";

const searchStore = useSearchStore();
const router = useRouter();

const showModal = ref(false);
const primeLocationName = ref("");
const address = ref("");
const pincode = ref("");
const price = ref("");
const maxSpots = ref("");
const parkingLots = ref([]);
const addFailMessage = ref("");

function searchResultIsNull(query) {
  const [_, value] = query.split('=');
  if (value === '') return true;
  return false;
}

async function fetchSearchResults(query) {
  const [key, value] = query.split("=");
  if (value === "") return fetchParkingLots();

  if (key.slice(0, 10) !== "parkingLot") router.push("users");

  const response = await axios.get(`/api/parking-lots/admin/search?${query}`);

  if (response.status == 200 && response.data.success)
    parkingLots.value = response.data.lots;
}

async function fetchParkingLots() {
  try {
    const response = await axios.get("/api/parking-lots/");
    if (response.status == 200 && response.data.success)
      parkingLots.value = response.data.lots;
    else parkingLots.value = [];
  } catch (error) {
    parkingLots.value = [];
  }
}

onMounted(async () => {
  await fetchSearchResults(searchStore.searchQuery);
});

watch(
  () => searchStore.searchQuery,
  (newQuery) => fetchSearchResults(newQuery)
);

async function handleAddLot() {
  try {
    const response = await axios.post("/api/parking-lots/", {
      primeLocationName: primeLocationName.value,
      address: address.value,
      pincode: String(pincode.value),
      price: price.value,
      maxSpots: maxSpots.value,
    });
    if (response.status == 201 && response.data.success) {
      showModal.value = false;
      primeLocationName.value = "";
      address.value = "";
      pincode.value = "";
      price.value = "";
      maxSpots.value = "";
      addFailMessage.value = "";
      await fetchParkingLots();
      toast.success(response.data.message);
    } else
      addFailMessage.value =
        response.data.message || "Failed to add parking lot";
  } catch (error) {
    addFailMessage.value =
      error.response?.data?.message ||
      "Unexpected error while adding parking lot";
  }
}
</script>

<template>
  <div class="vh-100" style="padding-top: 70px">
    <div
      class="container container-fluid overflow-auto"
      style="max-height: 100%"
    >
      <h1 class="text-center mb-4 pb-4 bg-white sticky-header">Parking Lots</h1>
      <div
        v-if="parkingLots.length"
        class="row g-4"
        style="display: flex; flex-wrap: wrap; margin-bottom: 80px"
      >
        <div
          v-for="lot in parkingLots"
          :key="lot.id"
          class="col-12 col-sm-6 col-md-4 col-lg-3"
          style="display: flex; justify-content: center; align-items: center"
        >
          <ParkingLotCard :lot="lot" @refresh="fetchParkingLots" />
        </div>
      </div>
      <div
        v-if="!parkingLots.length && searchResultIsNull(searchStore.searchQuery)"
        class="text-center w-100 h-100 overflow-hidden"
      >
        <img
          src="/images/sad_ghost.png"
          alt="No data found"
          style="width: 200px; height: 150px"
        />
        <p class="fs-3 text-muted">Nothing to show here</p>
      </div>
      <div
        v-if="!parkingLots.length && !searchResultIsNull(searchStore.searchQuery)"
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
    <div
      class="position-fixed bottom-0 d-flex justify-content-center py-2 vw-100 glass-background top-blur"
    >
      <button
        type="button"
        class="btn btn-lg btn-primary"
        @click="showModal = true"
      >
        <i class="bi bi-plus-lg"></i>
        Add Lot
      </button>
    </div>

    <BaseModal
      :show="showModal"
      title="New Parking Lot"
      @close="
        showModal = false;
        addFailMessage = '';
      "
      @submit="handleAddLot"
    >
      <template #body>
        <div v-if="addFailMessage" class="alert alert-danger" role="alert">
          <i class="bi bi-exclamation-triangle-fill"></i>
          {{ addFailMessage }}
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
            required
          />
        </div>
        <div class="mb-3">
          <label for="address" class="form-label">Address</label>
          <textarea
            v-model="address"
            id="address"
            class="form-control"
            required
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
            required
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
            required
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
            required
          />
        </div>
      </template>
      <template #footer>
        <button
          class="btn btn-outline-secondary"
          @click="
            showModal = false;
            addFailMessage = '';
          "
        >
          Cancel
        </button>
        <button type="submit" class="btn btn-success">Add Lot</button>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 2;
}

.glass-background {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.top-blur {
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}
</style>
