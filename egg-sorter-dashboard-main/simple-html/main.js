// database
config = config = {
  locateFile: (filename) => `/dist/${filename}`,
};

async function loadDatabase() {
  let totalEggs = 0;
  let weeklyEggs = 0;
  let monthlyEggs = 0;
  let dailyEggs = 0;
  let eggs = [];
  let eggSizes = [];

  const response = await fetch("app.db");
  const arrayBuffer = await response.arrayBuffer();
  const uint8Array = new Uint8Array(arrayBuffer);
  initSqlJs(config).then(function (SQL) {
    const db = new SQL.Database(uint8Array);

    const eggsStmt = db.prepare("SELECT * FROM eggs_tbl");
    while (eggsStmt.step()) {
      const row = eggsStmt.getAsObject();
      eggs.push(row); // Append the egg as an object (instead of manually converting)
    }
    totalEggs = eggs.length;
    eggsStmt.free(); // Free the statement

    // B. Calculate weekly eggs
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    const oneWeekAgoStr = oneWeekAgo
      .toISOString()
      .slice(0, 19)
      .replace("T", " "); // Format for SQLite

    const weeklyStmt = db.prepare(
      "SELECT COUNT(*) as count FROM eggs_tbl WHERE created_at >= ?"
    );
    weeklyStmt.bind([oneWeekAgoStr]); // Bind as an array (more reliable)
    if (weeklyStmt.step()) {
      weeklyEggs = weeklyStmt.getAsObject().count;
    }
    weeklyStmt.free();

    // C. Calculate monthly eggs
    const oneMonthAgo = new Date();
    oneMonthAgo.setDate(oneMonthAgo.getDate() - 30);
    const oneMonthAgoStr = oneMonthAgo
      .toISOString()
      .slice(0, 19)
      .replace("T", " ");

    const monthlyStmt = db.prepare(
      "SELECT COUNT(*) as count FROM eggs_tbl WHERE created_at >= ?"
    );
    monthlyStmt.bind([oneMonthAgoStr]);
    if (monthlyStmt.step()) {
      monthlyEggs = monthlyStmt.getAsObject().count;
    }
    monthlyStmt.free();

    // D. Calculate daily eggs
    const today = new Date().toISOString().slice(0, 10);
    const dailyStmt = db.prepare(
      "SELECT COUNT(*) as count FROM eggs_tbl WHERE DATE(created_at) = ?"
    );
    dailyStmt.bind([today]); // Bind as an array
    if (dailyStmt.step()) {
      dailyEggs = dailyStmt.getAsObject().count;
    }
    dailyStmt.free();

    // E. Egg Sizes
    const eggSizesStmt = db.prepare(
      "SELECT size, COUNT(*) as count FROM eggs_tbl GROUP BY size"
    );
    while (eggSizesStmt.step()) {
      const row = eggSizesStmt.getAsObject();
      eggSizes.push(row); // Append the size data as an object
    }
    eggSizesStmt.free();
    eggSizes = eggSizes.map((egg) => {
      return {
        name: egg.size,
        value: egg.count,
      };
    });

    // F. Weekly Chart Data
    let EggWeekDayCount = [0, 0, 0, 0, 0, 0, 0];
    for (let i = 0; i < eggs.length; i++) {
      const eggDate = new Date(eggs[i].created_at).getDay(); // Get the day of the week (0-6)
      EggWeekDayCount[eggDate]++;
    }

    const weightSeriesData = eggs.map((egg) => {
      return {
        x: new Date(egg.created_at).getTime(), // Use timestamp for datetime axis
        y: egg.weight,
      };
    });
    weightSeriesData.sort((a, b) => a.x - b.x);

    console.log(
      totalEggs,
      weeklyEggs,
      monthlyEggs,
      dailyEggs,
      eggs,
      weightSeriesData,
      eggSizes
    );

    // Update the HTML elements with the calculated values
    document.querySelector("#total-eggs").innerHTML = totalEggs;
    document.querySelector("#daily-eggs").innerHTML = dailyEggs;
    document.querySelector("#weekly-eggs").innerHTML = weeklyEggs;
    document.querySelector("#monthly-eggs").innerHTML = monthlyEggs;

    // Charts
    const options = {
      // 1. Series configuration
      series: [
        {
          name: "Egg Weight (g)", // More descriptive name
          data: weightSeriesData,
        },
      ],

      // 2. Chart Type and Appearance
      chart: {
        type: "line", // Line chart is often better for time-series data points
        height: 350,
        zoom: {
          // Enable zooming        enabled: true,
          type: "x",
          autoScaleYaxis: true, // Adjust Y-axis when zooming X
        },
        toolbar: {
          // Enable toolbar for zoom, pan, export
          show: false,
          tools: {
            download: true,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
            reset: true | '<img src="/static/icons/reset.png" width="20">', // Optional custom icon
            customIcons: [],
          },
          autoSelected: "zoom",
        },
      }, // 3. Data Labels (Keep disabled for cleaner look with many points)
      dataLabels: {
        enabled: false,
      },

      // 4. Stroke (Line Appearance)
      stroke: {
        curve: "smooth", // Smoother line visually
        width: 2, // Slightly thicker line
      },

      // 5. Markers (Show points on the line)
      markers: {
        size: 4, // Size of the markers
        hover: {
          size: 6, // Slightly larger marker on hover
        },
      },

      // 6. Tooltip Enhancements
      tooltip: {
        enabled: true,
        x: {
          format: "dd MMM yyyy, HH:mm", // Clearer date/time format
          // Use 'dd MMM yy, HH:mm' for shorter year
        },
        y: {
          formatter: function (val) {
            return val.toFixed(1) + " g"; // Add unit and format decimal
          },
          title: {
            // Consistent naming in tooltip
            formatter: (seriesName) => seriesName + ":",
          },
        },
        marker: {
          show: true,
        },
      },

      // 7. X-Axis Configuration
      xaxis: {
        type: "datetime", // Correct type for time series
        labels: {
          datetimeUTC: false, // Display in local time if server sends local time
          format: "dd MMM HH:mm", // Format for axis labels (adjust detail as needed)
        },
        title: {
          text: "Time Sorted", // Add axis title
          style: {
            fontSize: "12px",
            fontWeight: 600,
            color: "#555",
          },
        },
        tooltip: {
          // Prevent default x-axis tooltip competing with main tooltip
          enabled: false,
        },
      },

      // 8. Y-Axis Configuration
      yaxis: {
        title: {
          text: "Weight (grams)", // Add axis title
          style: {
            fontSize: "12px",
            fontWeight: 600,
            color: "#555",
          },
        },
        labels: {
          formatter: function (val) {
            return val.toFixed(1); // Consistent formatting
          },
        },
      },

      // 9. Grid Appearance
      grid: {
        borderColor: "#e7e7e7",
        row: {
          colors: ["#f3f3f3", "transparent"], // Zebra striping
          opacity: 0.5,
        },
      },
      // 11. Legend (Keep if needed, often redundant for single series)
      legend: {
        position: "top",
        horizontalAlign: "right",
        floating: true,
        offsetY: -25,
        offsetX: -5,
      },
    };
    const chart = new ApexCharts(
      document.querySelector("#reportsChart"),
      options
    );
    chart.render();

    // Recent Eggs Table
    const recentEggs = eggs
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5);
    const tableBody = document.getElementById("eggs-table-body");
    recentEggs.forEach((egg) => {
      const row = document.createElement("tr");
      row.innerHTML = `
              <th scope="row">#${egg.id}</th>
              <td>${egg.size}</td>
              <td>${egg.weight.toFixed(2)} g</td>
              <td>${new Date(egg.created_at).toLocaleDateString()}</td>
              <td>${new Date(egg.expected_expiry).toLocaleDateString()}</td>
          `;
      tableBody.appendChild(row);
    });

    // Right Chart
    echarts.init(document.querySelector("#trafficChart")).setOption({
      tooltip: {
        trigger: "item",
      },
      legend: {
        top: "5%",
        left: "center",
      },
      series: [
        {
          name: "Access From",
          type: "pie",
          radius: ["40%", "70%"],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: "center",
          },
          emphasis: {
            label: {
              show: true,
              fontSize: "18",
              fontWeight: "bold",
            },
          },
          labelLine: {
            show: false,
          },
          data: eggSizes,
        },
      ],
    });

    echarts.init(document.querySelector("#barChart")).setOption({
      xAxis: {
        type: "category",
        data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      },
      yAxis: {
        type: "value",
      },
      series: [
        {
          data: EggWeekDayCount,
          type: "bar",
        },
      ],
    });
  });
}

async function loadDatabase2() {
  let eggs = [];

  try {
    const response = await fetch("app.db");
    const arrayBuffer = await response.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);

    const SQL = await initSqlJs(config);
    const db = new SQL.Database(uint8Array);

    const eggsStmt = db.prepare(
      "SELECT * FROM eggs_tbl ORDER BY created_at DESC"
    );
    while (eggsStmt.step()) {
      const row = eggsStmt.getAsObject();
      eggs.push(row);
    }
    eggsStmt.free();

    const inventoryTableBody = document.getElementById("inventoryTableBody");

    eggs.forEach((egg) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${egg.size}</td>
        <td>${egg.weight}</td>
        <td>${new Date(egg.created_at).toLocaleDateString()}</td>
        <td>${new Date(egg.expected_expiry).toLocaleDateString()}</td>
      `;
      inventoryTableBody.appendChild(row);
    });

    const datatables = document.querySelectorAll(".datatable");
    datatables.forEach((datatable) => {
      new simpleDatatables.DataTable(datatable, {
        searchable: false,
        sortable: false,
        perPageSelect: [5, 10, 15, ["All", -1]],
        columns: [
          {
            select: 2,
            sortSequence: ["desc", "asc"],
          },
          {
            select: 3,
            sortSequence: ["desc", "asc"],
          },
          {
            select: 4,
            cellClass: "green",
            headerClass: "red",
          },
        ],
      });
    });
  } catch (error) {
    console.error("Error loading database:", error);
  }
}

if (window.location.pathname === "/simple-html/dashboard.html") {
  // Check if the user is logged in
  const cookies = document.cookie.split("; ");
  const loggedIn = cookies.find((cookie) => cookie.startsWith("loggedIn="));
  if (!loggedIn) {
    // If not logged in, redirect to login page
    window.location.href = "/simple-html/login.html";
  }
  loadDatabase();
}

if (window.location.pathname === "/simple-html/inventory.html") {
  // Check if the user is logged in
  const cookies = document.cookie.split("; ");
  const loggedIn = cookies.find((cookie) => cookie.startsWith("loggedIn="));
  if (!loggedIn) {
    // If not logged in, redirect to login page
    window.location.href = "/simple-html/login.html";
  }
  loadDatabase2();
}

if (window.location.pathname === "/simple-html/login.html") {
  const form = document.querySelector("form");
  console.log(form);
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const username = document.querySelector("#username").value;
    const password = document.querySelector("#password").value;

    if (username === "admin" && password === "admin") {
      document.cookie = "loggedIn=true; path=/"; // Set cookie for 1 day
      window.location.href = "/simple-html/dashboard.html"; // Redirect to dashboard
    } else {
      alert("Invalid username or password. Please try again.");
    }
  });
}

// sidebar
const sidebarToggle = document.querySelector(".toggle-sidebar-btn");

sidebarToggle.addEventListener("click", () => {
  document.body.classList.toggle("toggle-sidebar");
});
