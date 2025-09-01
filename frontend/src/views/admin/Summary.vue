<script setup>
import axios from "../../config/api";
import { onMounted, ref, watch } from "vue";
import { useSearchStore } from "../../stores/useSearchStore";
import { useRouter } from "vue-router";
import PieChart from "../../components/PieChart.vue";
import BarChart from "../../components/BarChart.vue";

const searchStore = useSearchStore();
const router = useRouter();

function redirectRoute(query) {
  const [key, value] = query.split("=");

  if (value === "") return;

  if (key.slice(0, 10) === "parkingLot") router.push("/");
  else router.push("/admin/users");
}

const revenueChart = ref({
  labels: [],
  datasets: [],
});
const statusChart = ref({
  labels: [],
  datasets: [],
});
const pieChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: "bottom" },
    title: {
      display: true,
      text: "Revenue Per Parking Lot",
      font: {
        size: 20,
        weight: "bold",
      },
      color: "black",
      padding: {
        top: 10,
        bottom: 20,
      },
    },
  },
});

const barChartOptions = ref({
  responsive: true,
  indexAxis: "y",
  maintainAspectRatio: false,
  plugins: {
    legend: { position: "bottom" },
    title: {
      display: true,
      text: "Parking Lot Status",
      font: {
        size: 20,
        weight: "bold",
      },
      color: "black",
      padding: {
        top: 10,
        bottom: 20,
      },
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text: "Number of Lots",
      },
      min: 0,
    },
  },
});

watch(
    () => searchStore.searchQuery,
    (newQuery) => redirectRoute(newQuery)
  );

onMounted(async () => {
  const response = await axios.get("/api/parking-lots/admin/summary");

  if (response.status != 200 || !response.data.success) return;

  const lots = response.data.lots;

  revenueChart.value = {
    labels: lots.filter((lot) => lot.revenue != 0.0).map((lot) => lot.name),
    datasets: [
      {
        label: "Revenue",
        data: lots.filter((lot) => lot.revenue != 0.0).map((lot) => lot.revenue),
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#8AFFC1",
          "#FFA07A",
        ],
      },
    ],
  };

  statusChart.value = {
    labels: lots.map((lot) => lot.name),
    datasets: [
      {
        label: "Occupied",
        data: lots.map((lot) => lot.occupied),
        backgroundColor: "#FF6384",
      },
      {
        label: "Available",
        data: lots.map((lot) => lot.available),
        backgroundColor: "#36A2EB",
      },
      {
        label: "Unavailable",
        data: lots.map((lot) => lot.unavailable),
        backgroundColor: "#ebd234",
      },
    ],
  };
});
</script>

<template>
  <div class="vh-100" style="padding-top: 70px">
    <div class="container">
      <div v-if="revenueChart.datasets.length || statusChart.datasets.length">
        <h1 class="text-center mb-4">Summary</h1>
        <div class="row">
          <div class="col-md-6" style="height: 70vh">
            <PieChart :chart-data="revenueChart" :options="pieChartOptions" />
          </div>
          <div class="col-md-6" style="height: 70vh">
            <BarChart :chart-data="statusChart" :options="barChartOptions" />
          </div>
        </div>
      </div>
      <div
        v-if="!revenueChart.datasets.length && !statusChart.datasets.length"
        class="text-center w-100 h-100 overflow-hidden"
      >
        <h1 class="text-center mb-4">Summary</h1>
        <img
          src="/images/sad_ghost.png"
          alt="No data found"
          style="width: 200px; height: 150px"
        />
        <p class="fs-3 text-muted">Nothing to show here</p>
      </div>
    </div>
  </div>
</template>
