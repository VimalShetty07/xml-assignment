import { BrowserRouter, Route, Routes } from "react-router-dom";
import { JobDetailPage } from "./pages/JobDetailPage";
import { JobsListPage } from "./pages/JobsListPage";
import { TaskDetailPage } from "./pages/TaskDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Routes>
          <Route path="/" element={<JobsListPage />} />
          <Route path="/jobs/:jobId" element={<JobDetailPage />} />
          <Route path="/jobs/:jobId/tasks/:taskId" element={<TaskDetailPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
