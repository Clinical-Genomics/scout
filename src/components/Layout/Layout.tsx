/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";
import Nav, { NavItem } from "components/Nav/Nav";
import styles from "./Layout.module.scss";
import logo_scout from "assets/logo_scout.png";
import logo_cg from "assets/logo_cg.svg";
import Footer from "components/Footer/Footer";

const header_cg = {
  icon: logo_cg,
  title: "Clinical Genomics",
};
const header_scout = {
  icon: logo_scout,
  title: "Scout",
};

const cgNavItems: Array<NavItem> = [
  { linkTitle: "Beställninger", public: true, link: "/orders" },
  { linkTitle: "Provkrav", public: true, link: "/requirements" },
  { linkTitle: "Applikationer", public: true, link: "/applications" },
  { linkTitle: "Dataleverans", public: true, link: "/delivery" },
  {
    linkTitle: "Support",
    public: true,
    dropdownList: [
      { linkTitle: "FAQ", public: true, link: "/faq" },
      { linkTitle: "Kontakt", public: true, link: "/contact" },
      { linkTitle: "Feedback", public: false, link: "/feedback" },
      { linkTitle: "Help", public: false, link: "/help" },
    ],
  },
  { linkTitle: "New order", public: false, link: "/new-order" },
  { linkTitle: "Status", public: false, link: "/status" },
  { linkTitle: "Items", public: false, link: "/items" },
];

const Layout: React.FC = ({ children }) => (
  <div className={styles.Layout}>
    <header>
      <Nav header={header_cg} navItems={cgNavItems} />
    </header>
    <main>{children}</main>
    <Footer />
  </div>
);

export default Layout;
