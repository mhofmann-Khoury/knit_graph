from unittest import TestCase

from knit_graphs.basic_knit_graph_generators import co_loops, jersey_swatch, jersey_tube, kp_rib_swatch, lace_mesh, seed_swatch


class TestCourse(TestCase):

    def test_co_loops_single_course(self):
        width = 6
        _, knit_graph, _ = co_loops(width)
        courses = knit_graph.get_courses()
        self.assertEqual(len(courses), 1)
        self.assertEqual(len(courses[0]), width)

    def test_flat_course_count_and_width(self):
        generators = [jersey_swatch, kp_rib_swatch, seed_swatch]
        width, height = 8, 6
        for gen in generators:
            with self.subTest(generator=gen.__name__):
                kg = gen(width, height)
                courses = kg.get_courses()
                self.assertEqual(len(courses), height + 1, f"{gen.__name__}: expected {height + 1} courses")
                for i, course in enumerate(courses):
                    self.assertEqual(len(course), width, f"{gen.__name__} course {i}: expected width {width}")

    def test_tube_course_count_and_width(self):
        width, height = 4, 4
        kg = jersey_tube(width, height)
        courses = kg.get_courses()
        self.assertEqual(len(courses), height)
        for i, course in enumerate(courses):
            self.assertEqual(len(course), width * 2, f"tube course {i}: expected width {width * 2}")

    def test_lace_course_count_and_width(self):
        width, height = 7, 4
        kg = lace_mesh(width, height)
        courses = kg.get_courses()
        self.assertEqual(len(courses), height * 2)
        for i, course in enumerate(courses):
            self.assertEqual(len(course), width, f"lace course {i}: expected width {width}")

    # --- course number ---

    def test_course_numbers_sequential(self):
        kg = jersey_swatch(5, 5)
        courses = kg.get_courses()
        for i, course in enumerate(courses):
            self.assertEqual(course.course_number, i)

    # --- in_row_with / in_round_with ---

    def test_flat_in_row_with(self):
        generators = [jersey_swatch, kp_rib_swatch, seed_swatch]
        for gen in generators:
            with self.subTest(generator=gen.__name__):
                kg = gen(6, 4)
                courses = kg.get_courses()
                for prior, nxt in zip(courses[:-1], courses[1:]):
                    self.assertTrue(prior.in_row_with(nxt), f"{gen.__name__}: {prior} not in_row_with {nxt}")

    def test_flat_not_in_round_with(self):
        generators = [jersey_swatch, kp_rib_swatch, seed_swatch]
        for gen in generators:
            with self.subTest(generator=gen.__name__):
                kg = gen(6, 4)
                courses = kg.get_courses()
                for prior, nxt in zip(courses[:-1], courses[1:]):
                    self.assertFalse(prior.in_round_with(nxt), f"{gen.__name__}: {prior} should not be in_round_with {nxt}")

    def test_tube_in_round_with(self):
        width, height = 4, 4
        kg = jersey_tube(width, height)
        courses = kg.get_courses()
        for prior, nxt in zip(courses[:-1], courses[1:]):
            self.assertTrue(prior.in_round_with(nxt), f"{prior} not in_round_with {nxt}")

    def test_tube_not_in_row_with(self):
        width, height = 4, 4
        kg = jersey_tube(width, height)
        courses = kg.get_courses()
        for prior, nxt in zip(courses[:-1], courses[1:]):
            self.assertFalse(prior.in_row_with(nxt), f"{prior} should not be in_row_with {nxt}")

    def test_flat_jersey_one_face_per_course(self):
        width, height = 5, 4
        kg = jersey_swatch(width, height)
        for course in kg.get_courses():
            faces = course.get_faces()
            self.assertEqual(len(faces), 1, f"{course}: expected 1 face, got {len(faces)}")
            self.assertTrue(faces[0].is_full_course)
            self.assertEqual(len(faces[0]), width)

    def test_tube_two_faces_per_course(self):
        width, height = 4, 2
        kg = jersey_tube(width, height)
        for course in kg.get_courses():
            faces = course.get_faces()
            self.assertEqual(len(faces), 2, f"{course}: expected 2 faces, got {len(faces)}")
            for face in faces:
                self.assertEqual(len(face), width, f"{course}: expected face width {width}")

    def test_face_loops_partition_course(self):
        """All loops in a course appear in exactly one face."""
        kg = jersey_tube(4, 3)
        for course in kg.get_courses():
            face_loops = [loop for face in course.get_faces() for loop in face]
            self.assertEqual(len(face_loops), len(course))
            self.assertEqual(set(face_loops), set(course))
