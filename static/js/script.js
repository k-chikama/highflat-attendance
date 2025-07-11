// 勤怠システム用のJavaScript

// ページ読み込み時の初期化（削除：下部で再定義）

// 自動保存機能（削除：下部で再定義）

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

// 打刻処理
function punch(field) {
  const today = new Date().toISOString().split("T")[0];

  // ローディング表示
  const button = document.querySelector(`button[onclick="punch('${field}')"]`);
  if (button) {
    button.disabled = true;
    button.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status"></span> 処理中...';
  }

  fetch("/api/punch", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      date: today,
      field: field,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showNotification(
          `${field === "check_in" ? "出勤" : "退勤"}を記録しました: ${
            data.time
          }`,
          "success"
        );

        // 画面の表示を更新
        updateDisplayTime(field, data.time);

        // 最新データで画面を更新
        if (data.updated_data) {
          updateTodayData(data.updated_data);
        }

        // 2秒後にページをリロード（最新データを確実に表示）
        setTimeout(() => {
          location.reload();
        }, 2000);
      } else {
        showNotification(
          "打刻に失敗しました: " + (data.error || "不明なエラー"),
          "danger"
        );
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification("打刻に失敗しました: " + error.message, "danger");
    })
    .finally(() => {
      // ボタンを元に戻す
      if (button) {
        button.disabled = false;
        button.innerHTML = field === "check_in" ? "出勤" : "退勤";
      }
    });
}

// 表示時間を更新
function updateDisplayTime(field, time) {
  const displayElement = document.getElementById(`${field}_display`);
  if (displayElement) {
    displayElement.textContent = time;
  }

  // 隠しフィールドも更新
  const hiddenField = document.querySelector(`input[name="${field}"]`);
  if (hiddenField) {
    hiddenField.value = time;
  }
}

// 今日のデータを更新
function updateTodayData(data) {
  // 出勤時間
  if (data.check_in) {
    updateDisplayTime("check_in", data.check_in);
  }

  // 退勤時間
  if (data.check_out) {
    updateDisplayTime("check_out", data.check_out);
  }

  // その他のフィールドも更新
  Object.keys(data).forEach((key) => {
    const element = document.getElementById(`${key}_display`);
    if (element) {
      element.textContent = data[key];
    }
  });
}

// フィールド保存処理
function saveField(date, field, value) {
  fetch("/api/save_field", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      date: date,
      field: field,
      value: value,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showNotification("データを保存しました", "success");
      } else {
        showNotification("保存に失敗しました", "danger");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification("保存に失敗しました: " + error.message, "danger");
    });
}

// 自動保存機能の改善
function setupAutoSave() {
  const inputs = document.querySelectorAll(
    'input[type="time"], input[type="text"], input[type="number"]'
  );
  let saveTimeout;

  inputs.forEach((input) => {
    input.addEventListener("change", function () {
      clearTimeout(saveTimeout);

      // フィールド名から日付とフィールドを抽出
      const name = this.name;
      if (name.includes("_")) {
        const parts = name.split("_");
        const field = parts[0];
        const date = parts.slice(1).join("_");

        saveTimeout = setTimeout(() => {
          saveField(date, field, this.value);
        }, 1000);
      }
    });
  });
}

// ページ読み込み時の初期化（更新）
document.addEventListener("DOMContentLoaded", function () {
  // フォームの自動保存機能
  setupAutoSave();

  // 入力フィールドのバリデーション
  setupValidation();

  // キーボードショートカット
  setupKeyboardShortcuts();

  // 5分ごとに最新データを取得
  setInterval(() => {
    refreshPageData();
  }, 5 * 60 * 1000);
});

// ページデータの更新
function refreshPageData() {
  // 現在のページが勤怠関連ページの場合のみ更新
  if (
    window.location.pathname.includes("/attendance") ||
    window.location.pathname === "/"
  ) {
    // 静かに最新データを取得
    fetch(window.location.href)
      .then((response) => response.text())
      .then((html) => {
        // 必要に応じて特定の部分のみ更新
        console.log("データを更新しました");
      })
      .catch((error) => {
        console.error("データ更新エラー:", error);
      });
  }
}
