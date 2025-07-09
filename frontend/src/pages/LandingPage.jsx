import React from "react";
import "../styles/LandingPage.css";
import { ReactComponent as NoAvatarLogo } from "../components/edHub_icon.svg"; 

export default function LandingPage() {
  return (
    <div className="landing-root">
      <header className="landing-header">
        <img className="landing-header-logo" />
        <nav className="landing-nav">
          <a href="#features">Features</a>
          <a href="#forwho">For Whom</a>
          <a href="#reviews">Reviews</a>
          <a href="/auth" className="landing-nav-btn">Log in</a>
        </nav>
      </header>
      <main className="landing-content">
        <section className="landing-mainblock">
          <div className="landing-mainblock-left">
            <div style={{ width: 180 }}>
              <NoAvatarLogo style={{width:"100%", height:"auto", display: "block"}} />
            </div>
            <p>
              Bringing together teachers, students, and parents in a single, user-friendly space for real progress and communication. All the tools for effective online learning, performance tracking, and seamless interaction.
            </p>
            <a href="/auth" className="landing-btn primary">Try for Free</a>
          </div>
          <div className="landing-mainblock-right">
            <img
              src="https://img.freepik.com/free-vector/online-tutorials-concept_52683-37480.jpg?w=900"
              alt="EdHub illustration"
              className="landing-illustration"
            />
          </div>
        </section>
        <section id="features" className="landing-section features">
          <h2>What Makes EdHub Special?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <img src="https://img.icons8.com/fluency/96/teacher.png" alt="" />
              <h3>For Teachers</h3>
              <p>Quickly create courses and assignments, manage classes, and monitor progress in just a few clicks.</p>
            </div>
            <div className="feature-card">
              <img src="https://img.icons8.com/fluency/96/student-male.png" alt="" />
              <h3>For Students</h3>
              <p>Instant access to all materials, easy homework submission, grades, and direct feedback.</p>
            </div>
            <div className="feature-card">
              <img src="https://img.icons8.com/fluency/96/family--v2.png" alt="" />
              <h3>For Parents</h3>
              <p>Stay updated on your child's achievements and support them without stress or guesswork.</p>
            </div>
            <div className="feature-card">
              <img src="https://img.icons8.com/fluency/96/checked-checkbox.png" alt="" />
              <h3>Transparency & Security</h3>
              <p>All data is protected and available only to authorized users. Your privacy is our priority.</p>
            </div>
          </div>
        </section>
        <section id="forwho" className="landing-section forwho">
          <h2>Who is EdHub for?</h2>
          <div className="forwho-grid">
            <div>
              <b>Schools & Teachers</b><br />
              Intuitive interface, course templates, automated reports, and journals.
            </div>
            <div>
              <b>Students of all ages</b><br />
              One space for all subjects, chat with teachers, and clear progress tracking.
            </div>
            <div>
              <b>Parents</b><br />
              See grades, assignments, and attendance — without bothering your child with extra questions.
            </div>
          </div>
        </section>
        <section className="landing-section promo">
          <div className="promo-grid">
            <div className="promo-card">
              <h3>1000+ Assignments Submitted</h3>
              <p>Our platform is already powering real education and real results.</p>
            </div>
            <div className="promo-card">
              <h3>Instant Start</h3>
              <p>Sign up in just one minute. No complicated steps — get started right away!</p>
            </div>
            <div className="promo-card">
              <h3>Absolutely Free</h3>
              <p>EdHub is open for all early users. Join and help us shape the future of learning!</p>
            </div>
          </div>
        </section>
        <section id="reviews" className="landing-section reviews">
          <h2>User Reviews</h2>
          <div className="reviews-grid">
            <div className="review-card">
              <div className="review-text">
                "It's so easy to track homework! EdHub really helps me stay on top of what's happening at school."
              </div>
              <div className="review-author">— Anna, Parent</div>
            </div>
            <div className="review-card">
              <div className="review-text">
                "Now all my assignments and materials are just one click away. I don't waste time searching for info!"
              </div>
              <div className="review-author">— Ilya, Student</div>
            </div>
            <div className="review-card">
              <div className="review-text">
                "EdHub saves me so much time and routine work. Everything just works, simply and quickly."
              </div>
              <div className="review-author">— Elena, Teacher</div>
            </div>
          </div>
        </section>
        <section className="landing-section cta">
  <h2>Join EdHub Today!</h2>
  <a href="/auth" className="landing-btn big">Get Started for Free</a>
  <div style={{ marginTop: 12, fontSize: "1rem" }}>
    <span>
      Project GitHub:{" "}
      <a href="https://github.com/IU-Capstone-Project-2025/edhub" target="_blank" rel="noopener noreferrer">
        github.com/IU-Capstone-Project-2025/edhub
      </a>
    </span>
  </div>
</section>

      </main>
      <footer className="landing-footer">
        &copy; {new Date().getFullYear()} EdHub. All rights reserved.
      </footer>
    </div>
  );
}
