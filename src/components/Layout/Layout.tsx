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

const navLinks: Array<NavItem> = [
  { linkTitle: "Beställninger", link: "/bestallningar" },
  { linkTitle: "Provkrav", link: "/provkrav" },
  { linkTitle: "Applikationer", link: "/applikationer" },
  { linkTitle: "Dataleverans", link: "/dataleverans" },
  { linkTitle: "FAQ", link: "/faq" },
  { linkTitle: "Kontakt", link: "/kontakt" },
  {
    linkTitle: "More",
    dropdownList: [
      { linkTitle: "test dropdown 1", link: "test" },
      { linkTitle: "test dropdown 2", link: "test" },
      { linkTitle: "test dropdown 3", link: "test" },
    ],
  },
];

const Layout: React.FC = ({ children }) => (
  <div className={styles.Layout}>
    <header>
      <Nav header={header_scout} navLinks={navLinks} />
    </header>
    <main>{children}</main>
    <Footer />
  </div>
);

export default Layout;
