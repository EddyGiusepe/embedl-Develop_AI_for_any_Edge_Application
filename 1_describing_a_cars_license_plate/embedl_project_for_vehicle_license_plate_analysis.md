<h1 align="center"><font color="gree">Vehicle License Plate Analysis with Embedl Edge AI</font></h1>


## <font color="red">Author</font>

`Senior Data Scientist:` Dr. Eddy Giusepe Chirinos Isidro

`GitHub:` EddyGiusepe

`Email:` eddychirinos.unac@gmail.com

This project is an **Edge AI** application for analyzing vehicle license plates in images and videos using an Embedl Vision Language Model. The goal is to perform inference locally on the device, without relying on cloud services to analyze the media sent by the user.

This project was developed considering the challenge [Edge AI Application of the Month](https://www.embedl.com/knowledge/edge-ai-application-of-the-month), which values real-world AI applications running on local hardware, with public code, practical demonstration and a write-up that explains the problem, the chosen model, the architecture and the results.

## <font color="red">Project Demo</font>

**Demo video:** [Watch on LinkedIn](https://www.linkedin.com/posts/SEU_LINK_AQUI)

The demo video is published on LinkedIn and shows the complete flow of the application:

1. Backend FastAPI running locally.
2. Frontend React accessed by the browser.
3. Upload of an image or video containing a vehicle with a license plate.
4. Inference executed locally with the Embedl model.
5. Structured result displayed in the interface.

To align with the Embedl challenge, the demo should demonstrate that the model is running on the same device, for example on a laptop, Raspberry Pi, Jetson or other local hardware.

## <font color="red">Features</font>

- Upload of images and videos containing vehicles with license plates.
- Preview of the media before analysis.
- Asynchronous processing in the backend using memory jobs.
- Automatic polling in the frontend to track the analysis status.
- Support for images and videos.
- Extraction of descriptive information from the plate, such as country, number, region, format, visual characteristics, vehicle and confidence level.
- Support for multiple plates in videos, when the model identifies more than one plate.
- Structured prompts to reduce hallucination and guide the model to respond carefully.
- Parser in the frontend to transform the model's response into structured blocks in the interface.
- Fallback to display the original model response when the expected format is not recognized.

## <font color="red">Model Used</font>

The model used is the **`embedl/Cosmos-Reason2-2B-W4A16`**, configured in the backend as the main application model.

This model is a **Vision Language Model (VLM)** from Embedl optimized for Edge AI scenarios. The **W4A16** version uses 4-bit weights and 16-bit activations, reducing memory consumption compared to larger models without quantization.

In this project, the model is used to analyze vehicle license plates visually and generate a structured response with:

- Country or likely origin of the plate.
- Plate number read by the model.
- State, city or region, when visible.
- Plate format.
- Visual characteristics, such as colors, symbols, flags or stripes.
- Vehicle information, when identifiable.
- Confidence level of the analysis.

The backend allows configuring the execution device with `DEVICE=auto`, `cuda`, `cpu` or `mps`, as well as configuring the data type with `DTYPE=auto`. This facilitates testing the application in different local environments.

## <font color="red">Tech Stack</font>

**Backend**

- Python 3.13
- FastAPI
- Uvicorn
- PyTorch
- Transformers
- Accelerate
- OpenCV
- Pillow
- Pydantic Settings
- Python Multipart

**Frontend**

- React 19
- TypeScript
- Vite 6
- TailwindCSS v4
- shadcn/ui
- TanStack Query v5
- sonner
- lucide-react

**Architecture**

- API REST for upload and query of jobs.
- Background processing with `BackgroundTasks` from FastAPI.
- Storage of jobs in memory.
- Temporary uploads in `backend_embedl/data/uploads`.
- Frontend with automatic polling to track progress.
- Proxy of Vite for local integration between frontend and backend.

## <font color="red">How to Run Locally</font>

Execute the backend and the frontend in separate terminals.

### <font color="blue">Backend</font>

In the root of the repository, install the Python dependencies:

```bash
uv sync
```

Then, start the API:

```bash
cd 1_describing_a_cars_license_plate/backend_embedl
./run.sh
```

The backend will be available at:

- API: `http://localhost:8000`
- Swagger Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### <font color="blue">Frontend</font>

In another terminal, install the frontend dependencies and start the development server:

```bash
cd 1_describing_a_cars_license_plate/frontend_embedl
npm install
npm run dev
```

The frontend will be available at:

- App: `http://localhost:5173`

By default, the frontend uses the Vite proxy to forward calls `/api/*` and `/health` to the local backend at `http://localhost:8000`.

## <font color="red">Highlights</font>

### <font color="blue">Technical Depth</font>

- Use of an Embedl model optimized for Edge AI: `embedl/Cosmos-Reason2-2B-W4A16`.
- Local inference, without depending on external computer vision APIs.
- Model loaded once in memory to avoid reloading on each request.
- Flexible configuration of device and data type via `.env`.
- Pipeline for images and videos.
- Asynchronous processing to keep the API responsive during inference.
- Memory cleanup after the analysis execution.
- Centralized and structured prompts to improve consistency, caution and response format.
- Resilient parser in the frontend to handle small variations in the model's textual output.

### <font color="blue">Creativity</font>

The project applies a lightweight `VLM` optimized for Edge AI to a practical visual case: vehicle license plate analysis. Instead of just detecting objects, the application generates an interpretable description of the plate and visual context, including format, likely country, read characters, visual characteristics and vehicle.

This approach is useful for scenarios like security prototypes, access control, video triage, local inspection and applications where privacy and low latency are important.

### <font color="blue">Community Impact</font>

The project was organized as a demonstrable full-stack application, with backend, frontend and documentation separated. This facilitates reproduction by other people interested in Edge AI, small VLMs, local inference and computer vision applications.

The write-up also serves as material to show how to integrate an Embedl model into a practical application with web interface, local API and asynchronous processing.

### <font color="blue">Alignment with the Challenge</font>

This project addresses the main points of the **Edge AI Application of the Month** challenge:

- Uses an Embedl model available on Hugging Face.
- Thought for local inference on real hardware.
- Resolves a practical visual problem with real-world application.
- Includes organized code for backend and frontend.
- Will have a public demo video showing the complete flow.
- Explains the chosen model, architecture and technical components of the solution.



Thank God! 💖