import cv2
import mediapipe as mp
import numpy as np

import csv
import datetime
import threading

# Init MediaPipe & FER
mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
mp_pose = mp.solutions.pose.Pose()
emotion_detector = FER(mtcnn=True)

# Report file
REPORT_FILE = "confidence_reports.csv"

# App Class
class ConfidenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Confidence Analyzer - Interview Tool")
        self.root.geometry("500x400")

        self.label = tk.Label(root, text="Confidence Analyzer", font=("Arial", 18))
        self.label.pack(pady=15)

        self.name_entry_label = tk.Label(root, text="Candidate Name:")
        self.name_entry_label.pack()
        self.name_entry = tk.Entry(root, width=30)
        self.name_entry.pack(pady=5)

        self.live_btn = tk.Button(root, text="Start Live Analysis", command=self.start_live_analysis)
        self.live_btn.pack(pady=15)

        self.result_label = tk.Label(root, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

        self.leaderboard_btn = tk.Button(root, text="Show Leaderboard", command=self.show_leaderboard)
        self.leaderboard_btn.pack(pady=10)

    def start_live_analysis(self):
        threading.Thread(target=self.live_analysis).start()

    def live_analysis(self):
        candidate_name = self.name_entry.get().strip()
        if not candidate_name:
            messagebox.showwarning("Input Error", "Please enter candidate name.")
            return

        cap = cv2.VideoCapture(0)
        frame_count = 0
        emotion_scores = []
        face_forward_count = 0
        good_posture_count = 0

        self.result_label.config(text="Analyzing live... Press 'q' to finish.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = mp_face_mesh.process(rgb_frame)
            pose_results = mp_pose.process(rgb_frame)

            emotions = emotion_detector.detect_emotions(frame)
            if emotions:
                dominant_emotion = emotions[0]['emotions']
                score = dominant_emotion.get('happy', 0) - dominant_emotion.get('fear', 0)
                emotion_scores.append(score)

            if face_results.multi_face_landmarks:
                face_forward_count += 1

            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                left_shoulder = landmarks[11]
                right_shoulder = landmarks[12]
                head = landmarks[0]

                shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
                head_to_shoulder = abs(head.y - ((left_shoulder.y + right_shoulder.y) / 2))
                if shoulder_diff < 0.05 and head_to_shoulder < 0.3:
                    good_posture_count += 1

            cv2.imshow("Live Confidence Analysis - Press 'q' to stop", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        emotion_score = np.mean(emotion_scores) * 100 if emotion_scores else 0
        face_ratio = face_forward_count / frame_count * 100
        posture_ratio = good_posture_count / frame_count * 100

        final_score = (emotion_score * 0.5) + (face_ratio * 0.25) + (posture_ratio * 0.25)
        final_score = round(np.clip(final_score, 0, 100), 2)

        verdict = "✅ Highly Confident" if final_score >= 75 else \
                  "⚖️ Moderately Confident" if final_score >= 50 else "❌ Low Confidence"

        self.result_label.config(text=f"{candidate_name}'s Score: {final_score}%\nVerdict: {verdict}")

        # Save Report
        self.save_report(candidate_name, final_score, verdict)

    def save_report(self, name, score, verdict):
        file_exists = False
        try:
            with open(REPORT_FILE, 'r'):
                file_exists = True
        except FileNotFoundError:
            pass

        with open(REPORT_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Candidate', 'Score', 'Verdict', 'DateTime'])
            writer.writerow([name, score, verdict, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        messagebox.showinfo("Report Saved", f"{name}'s result saved!")

    def show_leaderboard(self):
        leaderboard_win = tk.Toplevel(self.root)
        leaderboard_win.title("Leaderboard")
        leaderboard_win.geometry("400x300")

        tk.Label(leaderboard_win, text="Top Candidates", font=("Arial", 14)).pack(pady=10)

        listbox = tk.Listbox(leaderboard_win, width=50)
        listbox.pack(pady=10)

        try:
            with open(REPORT_FILE, 'r') as file:
                reader = csv.DictReader(file)
                scores = sorted(reader, key=lambda x: float(x['Score']), reverse=True)
                for row in scores[:10]:  # Top 10
                    listbox.insert(tk.END, f"{row['Candidate']} - {row['Score']}% - {row['Verdict']}")
        except FileNotFoundError:
            listbox.insert(tk.END, "No reports found.")

# Run App
root = tk.Tk()
app = ConfidenceApp(root)
root.mainloop()
