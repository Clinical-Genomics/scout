import React from "react";
import styles from "./DropdownMenu.module.scss";

const DropdownMenu: React.FC = ({ children }) => (
  <ul className={`${styles.DropdownMenu} dropdown_menu`}>{children}</ul>
);
export default DropdownMenu;
