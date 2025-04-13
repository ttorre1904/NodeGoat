const {
    BenefitsDAO
} = require("../data/benefits-dao");
const {
    environmentalScripts
} = require("../../config/config");

function BenefitsHandler(db) {
    "use strict";

    const benefitsDAO = new BenefitsDAO(db);

    // Middleware to check if the user is an admin
    const isAdmin = (req, res, next) => {
        if (req.session.user && req.session.user.isAdmin) {
            next();
        } else {
            return res.status(403).json({ error: "Unauthorized access. Admin rights required." });
        }
    };

    this.displayBenefits = (req, res, next) => {
        // Apply admin check
        if (!req.session.user || !req.session.user.isAdmin) {
            return res.status(403).render("403");
        }

        benefitsDAO.getAllNonAdminUsers((error, users) => {
            if (error) return next(error);

            return res.render("benefits", {
                users,
                user: req.session.user,
                environmentalScripts
            });
        });
    };

    this.updateBenefits = (req, res, next) => {
        // Apply admin check
        if (!req.session.user || !req.session.user.isAdmin) {
            return res.status(403).render("403");
        }

        const {
            userId,
            benefitStartDate
        } = req.body;

        // Validate inputs
        if (!userId || !benefitStartDate) {
            return res.status(400).json({ error: "Missing required parameters" });
        }

        benefitsDAO.updateBenefits(userId, benefitStartDate, (error) => {

            if (error) return next(error);

            benefitsDAO.getAllNonAdminUsers((error, users) => {
                if (error) return next(error);

                const data = {
                    users,
                    user: {
                        isAdmin: true
                    },
                    updateSuccess: true,
                    environmentalScripts
                };

                return res.render("benefits", data);
            });
        });
    };
}

module.exports = BenefitsHandler;
