# Copyright (c) 2021, ruthra and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document


class LibraryTransaction(Document):
        def before_submit(self):
                if self.type == "Issue":
                        self.validate_issue()
                        self.validate_maximum_limit()
                        
                        article = frappe.get_doc("Article", self.article)
                        article.status = "Issued"
                        article.save()

                elif self.type == "Return":
                        self.validate_return()

                        article = frappe.get_doc("Article", self.article)
                        article.status = "Available"
                        article.save()

        def validate_maximum_limit(self):
                max_articles = frappe.db.get_single_value("Library Settings", "max_articles")
                count = frappe.db.count(
                        "Library Transaction",
                        {"library_member":  self.library_member, "type": "Issue", "docstatus": 1},
                )

                if count >= max_articles:
                        frappe.throw("Maximum limit reached for issuing articles")

        def validate_issue(self):
                self.validate_membership()
                article = frappe.get_doc("Article", self.article)
                if article.status == "Issued":
                        frappe.throw("Article is already issued to another member")

        def validate_return(self):
                self.validate_membership()
                article = frappe.get_doc("Article", self.article)
                if article.status == "Available":
                        frappe.throw("Article cannot be returned without being issued first")

        def validate_membership(self):
                validate_membership = frappe.db.exists(
                        "Library Membership",
                        {
                                "library_member": self.library_member,
                                "docstatus": 1,
                                "from_date": ("<", self.date),
                                "to_date": (">", self.date),
                        },
                )

                if not validate_membership:
                        frappe.throw("The member does not have a valid membership")
