# controller.py
from flask import render_template, redirect, url_for, request

def register_routes(app, model):

    @app.route("/")
    def accueil():
        attractions = model.liste_attractions()
        return render_template("accueil.html", attractions=attractions, active="caisse")

    @app.route("/vendre/<int:attraction_id>", methods=["POST"])
    def vendre(attraction_id):
        try:
            quantite = int(request.form.get("quantite", 1))
        except ValueError:
            quantite = 1
        if quantite < 1:
            quantite = 1
        if quantite > 20:
            quantite = 20

        tickets = model.vendre_ticket(attraction_id, quantite)
        if tickets is None:
            return redirect(url_for("accueil"))
        return render_template("ticket.html", tickets=tickets)

    @app.route("/rapport")
    def rapport():
        stats = model.total_du_jour()
        details = model.total_par_attraction_jour()
        tickets = model.tickets_du_jour()
        return render_template("rapport.html", stats=stats, details=details, tickets=tickets, active="rapport")

    @app.route("/historique")
    def historique():
        jours = model.liste_jours()
        return render_template("historique.html", jours=jours, active="historique")

    @app.route("/historique/<jour>")
    def detail_jour(jour):
        tickets = model.tickets_par_jour(jour)
        details = model.total_par_attraction_pour_jour(jour)
        total_tickets = len(tickets)
        total_argent = sum(t[3] for t in tickets)
        return render_template("detail_jour.html", jour=jour, tickets=tickets,
                                details=details, total_tickets=total_tickets, total_argent=total_argent, active="historique")