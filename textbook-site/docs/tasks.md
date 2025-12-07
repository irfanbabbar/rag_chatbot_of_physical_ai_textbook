# Tasks: Physical AI & Humanoid Robotics Textbook

**Input**: Design documents from `/specs/001-ai-robotics-textbook/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The feature specification did not explicitly request test tasks, so none are included here.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create a new Docusaurus project in the root directory
- [ ] T002 Configure `docusaurus.config.js` for basic project metadata, sidebar, and plugins
- [ ] T003 [P] Setup custom CSS for educational content in `src/css/custom.css`
- [ ] T004 [P] Integrate Algolia DocSearch (requires Algolia credentials) in `docusaurus.config.js`
- [ ] T005 [P] Configure Prism for code syntax highlighting in `docusaurus.config.js`
- [ ] T006 [P] Enable Mermaid diagrams in `docusaurus.config.js`
- [ ] T007 [P] Configure GitHub Pages deployment in `.github/workflows/deploy.yml`
- [ ] T008 [P] Set up automated CI/CD with GitHub Actions in `.github/workflows/ci.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core content structure and asset management that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Create the main `docs/` directory for textbook content
- [ ] T010 Create `docs/module1/`, `docs/module2/`, `docs/module3/`, `docs/module4/` directories
- [ ] T011 Create weekly subdirectories within each module (e.g., `docs/module1/week3/`, `docs/module1/week4/`, `docs/module1/week5/`)
- [ ] T012 Create `src/components/` for custom React components
- [ ] T013 Create `src/theme/` for Docusaurus theme overrides
- [ ] T014 Create `static/` for static assets like images, diagrams, and PDFs
- [ ] T015 [P] Implement dark/light theme toggle in `src/theme/Toggle/index.js` (if overriding)
- [ ] T016 [P] Ensure mobile-responsive design with initial CSS adjustments in `src/css/custom.css`
- [ ] T017 [P] Refine sidebar navigation structure in `docusaurus.config.js` to reflect modules and weeks

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Learning ROS 2 Fundamentals (Priority: P1) 🎯 MVP

**Goal**: Students understand ROS 2 core concepts and Python integration for basic robotic applications.

**Independent Test**: A student can successfully implement and run a simple ROS 2 publisher-subscriber system in Python based on the textbook.

### Implementation for User Story 1

- [ ] T018 [P] [US1] Create `docs/module1/week3.mdx` for ROS 2 architecture, nodes, topics, services
- [ ] T019 [P] [US1] Add content for Python integration with `rclpy` in `docs/module1/week4.mdx`
- [ ] T020 [P] [US1] Add content for URDF for humanoid robots in `docs/module1/week5.mdx`
- [ ] T021 [US1] Include code examples for ROS 2 concepts in `docs/module1/week3.mdx`, `week4.mdx`, `week5.mdx`
- [ ] T022 [P] [US1] Add diagrams for ROS 2 architecture and URDF in `static/assets/module1/`
- [ ] T023 [US1] Add practical exercises for ROS 2 fundamentals in `docs/module1/`
- [ ] T024 [P] [US1] Define learning objectives for Module 1 in `docs/module1/_category_.json`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Simulating Digital Twins (Priority: P1)

**Goal**: Students learn to create and simulate digital twins in Gazebo and Unity with physics and sensor simulations.

**Independent Test**: A student can successfully launch a simulated humanoid robot in both Gazebo and Unity, demonstrating basic movement and sensor data visualization.

### Implementation for User Story 2

- [ ] T025 [P] [US2] Create `docs/module2/week6.mdx` for physics simulation in Gazebo
- [ ] T026 [P] [US2] Add content for high-fidelity rendering in Unity in `docs/module2/week7.mdx`
- [ ] T027 [US2] Add content for sensor simulation (LiDAR, cameras, IMUs) for Module 2 in `docs/module2/week6.mdx`, `week7.mdx`
- [ ] T028 [US2] Include code examples for Gazebo/Unity simulation in `docs/module2/`
- [ ] T029 [P] [US2] Add diagrams for simulation concepts and sensor data in `static/assets/module2/`
- [ ] T030 [US2] Add practical exercises for digital twin simulation in `docs/module2/`
- [ ] T031 [P] [US2] Define learning objectives for Module 2 in `docs/module2/_category_.json`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Developing AI Robot Brains with NVIDIA Isaac (Priority: P2)

**Goal**: Students understand and apply NVIDIA Isaac for advanced AI-robot brain development.

**Independent Test**: A student can successfully implement a simple navigation task for a bipedal robot using Isaac Sim and Isaac ROS, demonstrating VSLAM and Nav2 integration.

### Implementation for User Story 3

- [ ] T032 [P] [US3] Create `docs/module3/week8.mdx` for Isaac Sim for photorealistic simulation
- [ ] T033 [P] [US3] Add content for Isaac ROS (VSLAM and navigation) in `docs/module3/week9.mdx`
- [ ] T034 [P] [US3] Add content for Nav2 for bipedal movement in `docs/module3/week10.mdx`
- [ ] T035 [US3] Include code examples for NVIDIA Isaac platforms in `docs/module3/`
- [ ] T036 [P] [US3] Add diagrams for Isaac Sim, Isaac ROS, and Nav2 workflows in `static/assets/module3/`
- [ ] T037 [US3] Add practical exercises for NVIDIA Isaac development in `docs/module3/`
- [ ] T038 [P] [US3] Define learning objectives for Module 3 in `docs/module3/_category_.json`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Vision-Language-Action (VLA) Integration (Priority: P2)

**Goal**: Students learn to integrate VLA capabilities and complete an autonomous humanoid capstone project.

**Independent Test**: A student can implement a basic VLA pipeline where a robot responds to a simple voice command by performing a planned physical action in simulation.

### Implementation for User Story 4

- [ ] T039 [P] [US4] Create `docs/module4/week11.mdx` for voice commands with OpenAI Whisper
- [ ] T040 [P] [US4] Add content for LLM cognitive planning in `docs/module4/week12.mdx`
- [ ] T041 [P] [US4] Outline Capstone project: Autonomous Humanoid in `docs/module4/week13.mdx`
- [ ] T042 [US4] Include code examples for VLA integration in `docs/module4/`
- [ ] T043 [P] [US4] Add diagrams for VLA architecture and capstone project overview in `static/assets/module4/`
- [ ] T044 [US4] Add practical exercises for VLA integration in `docs/module4/`
- [ ] T045 [P] [US4] Define learning objectives for Module 4 in `docs/module4/_category_.json`

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T046 Add Course overview and learning outcomes in `docs/intro.mdx`
- [ ] T047 Add Assessment guidelines in `docs/assessment.mdx`
- [ ] T048 Add Hardware requirements section in `docs/hardware.mdx`
- [ ] T049 Add Prerequisites and setup instructions in `docs/setup.mdx`
- [ ] T050 Create Glossary and additional resources in `docs/glossary.mdx`
- [ ] T051 Ensure all Admonitions (tips, warnings) are consistently applied across content
- [ ] T052 Implement tabs for different code examples (Python, C++) where relevant in content files
- [ ] T053 Review and optimize content for accessibility and readability
- [ ] T054 Validate all internal links and navigation within the Docusaurus site

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable

### Within Each User Story

- Content creation before code examples/diagrams for that section.
- Code examples before practical exercises.
- Define learning objectives for a module after its content is structured.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Creation of weekly `.mdx` files within a module can be parallelized.
- Different user stories can be worked on in parallel by different team members.
- Adding diagrams and code examples for different sections can be parallelized.

---

## Parallel Example: User Story 1

```bash
# Create content files for User Story 1:
Task: "Create docs/module1/week3.mdx for ROS 2 architecture, nodes, topics, services"
Task: "Add content for Python integration with rclpy in docs/module1/week4.mdx"
Task: "Add content for URDF for humanoid robots in docs/module1/week5.mdx"

# Add diagrams and define learning objectives (can be parallel with content creation):
Task: "Add diagrams for ROS 2 architecture and URDF in static/assets/module1/"
Task: "Define learning objectives for Module 1 in docs/module1/_category_.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (ROS 2)
   - Developer B: User Story 2 (Digital Twin)
   - Developer C: User Story 3 (NVIDIA Isaac)
   - Developer D: User Story 4 (VLA)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
