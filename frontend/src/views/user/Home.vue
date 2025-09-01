<script setup>
import { ref } from "vue";
import RecentParkingHistory from "../../components/RecentParkingHistory.vue";
import BookParkingLots from "../../components/BookParkingLots.vue";
import axios from "../../config/api";

const reservations = ref([]);

async function getParkingHistory() {
  const response = await axios.get("/api/reservations/");

  if (response.status == 200 && response.data.success)
    reservations.value = response.data.reservations;
  else reservations.value = [];
}
</script>

<template>
  <div class="vh-100" style="padding-top: 56px;">
    <RecentParkingHistory :reservations @refresh="getParkingHistory" />
    <BookParkingLots @refresh="getParkingHistory" />
  </div>
</template>
