// 勤怠システム用のJavaScript

// ページ読み込み時の初期化
document.addEventListener("DOMContentLoaded", function () {
  // フォームの自動保存機能
  setupAutoSave();

  // 入力フィールドのバリデーション
  setupValidation();

  // キーボードショートカット
  setupKeyboardShortcuts();
});

// 自動保存機能
function setupAutoSave() {
  const inputs = document.querySelectorAll(
    'input[type="time"], input[type="text"]'
  );
  let saveTimeout;

  inputs.forEach((input) => {
    input.addEventListener("change", function () {
      clearTimeout(saveTimeout);
      saveTimeout = setTimeout(() => {
        showNotification("データを自動保存しました", "success");
      }, 1000);
    });
  });
}

// バリデーション機能
function setupValidation() {
  const timeInputs = document.querySelectorAll('input[type="time"]');

  timeInputs.forEach((input) => {
    input.addEventListener("blur", function () {
      validateTimeInput(this);
    });
  });
}

// 時間入力のバリデーション
function validateTimeInput(input) {
  const value = input.value;
  if (value) {
    const time = new Date(`2000-01-01T${value}`);
    if (isNaN(time.getTime())) {
      input.classList.add("is-invalid");
      showNotification("正しい時間形式で入力してください (HH:MM)", "warning");
    } else {
      input.classList.remove("is-invalid");
    }
  }
}

// キーボードショートカット
function setupKeyboardShortcuts() {
  document.addEventListener("keydown", function (e) {
    // Ctrl+S で保存
    if (e.ctrlKey && e.key === "s") {
      e.preventDefault();
      const saveButton = document.querySelector('button[type="submit"]');
      if (saveButton) {
        saveButton.click();
      }
    }

    // Ctrl+E でExcel出力
    if (e.ctrlKey && e.key === "e") {
      e.preventDefault();
      const excelButton = document.querySelector('a[href*="export_excel"]');
      if (excelButton) {
        excelButton.click();
      }
    }
  });
}

// 通知表示機能
function showNotification(message, type = "info") {
  // 既存の通知を削除
  const existingNotification = document.querySelector(".notification");
  if (existingNotification) {
    existingNotification.remove();
  }

  // 新しい通知を作成
  const notification = document.createElement("div");
  notification.className = `notification alert alert-${type} alert-dismissible fade show position-fixed`;
  notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    `;

  notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  document.body.appendChild(notification);

  // 3秒後に自動削除
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 3000);
}

// 勤務時間の計算（詳細版）
function calculateDetailedWorkHours(dateStr) {
  const checkIn = document.querySelector(
    `input[name="check_in_${dateStr}"]`
  ).value;
  const checkOut = document.querySelector(
    `input[name="check_out_${dateStr}"]`
  ).value;

  if (checkIn && checkOut) {
    const start = new Date(`2000-01-01T${checkIn}`);
    const end = new Date(`2000-01-01T${checkOut}`);

    // 日をまたぐ場合の処理
    if (end < start) {
      end.setDate(end.getDate() + 1);
    }

    const diffMs = end - start;
    const diffHours = diffMs / (1000 * 60 * 60);

    // 勤務時間を設定
    document.querySelector(`input[name="work_hours_${dateStr}"]`).value =
      diffHours.toFixed(1);

    // 実働時間と残業時間を計算
    calculateActualHours(dateStr);

    // 長時間勤務の警告
    if (diffHours > 12) {
      showNotification(
        "長時間勤務が検出されました。休憩時間を確認してください。",
        "warning"
      );
    }
  }
}

// 月次統計の計算
function calculateMonthlyStats() {
  const actualHoursInputs = document.querySelectorAll(
    'input[name*="actual_hours"]'
  );
  const overtimeHoursInputs = document.querySelectorAll(
    'input[name*="overtime_hours"]'
  );

  let totalActualHours = 0;
  let totalOvertimeHours = 0;
  let workDays = 0;

  actualHoursInputs.forEach((input) => {
    const hours = parseFloat(input.value) || 0;
    if (hours > 0) {
      totalActualHours += hours;
      workDays++;
    }
  });

  overtimeHoursInputs.forEach((input) => {
    const hours = parseFloat(input.value) || 0;
    totalOvertimeHours += hours;
  });

  // 統計情報を表示
  const statsHtml = `
        <div class="row mt-3">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">総実働時間</h5>
                        <p class="card-text h4 text-primary">${totalActualHours.toFixed(
                          1
                        )}時間</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">総残業時間</h5>
                        <p class="card-text h4 text-danger">${totalOvertimeHours.toFixed(
                          1
                        )}時間</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">出勤日数</h5>
                        <p class="card-text h4 text-success">${workDays}日</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">平均実働時間</h5>
                        <p class="card-text h4 text-info">${
                          workDays > 0
                            ? (totalActualHours / workDays).toFixed(1)
                            : 0
                        }時間</p>
                    </div>
                </div>
            </div>
        </div>
    `;

  // 統計情報を表示する場所があれば更新
  const statsContainer = document.getElementById("monthly-stats");
  if (statsContainer) {
    statsContainer.innerHTML = statsHtml;
  }
}

// データのエクスポート機能
function exportData() {
  const table = document.querySelector("table");
  const rows = Array.from(table.querySelectorAll("tr"));

  let csvContent = "data:text/csv;charset=utf-8,";

  rows.forEach((row) => {
    const cells = Array.from(row.querySelectorAll("th, td"));
    const rowData = cells.map((cell) => {
      const input = cell.querySelector("input");
      return input ? input.value : cell.textContent.trim();
    });
    csvContent += rowData.join(",") + "\n";
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "attendance_data.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showNotification("CSVファイルをダウンロードしました", "success");
}
