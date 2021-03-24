from django.core.management.base import BaseCommand

from shop import models
from shop.client import iiko


class Command(BaseCommand):
    help = "Synchronize stock with IIKO"

    def handle(self, *args, **options):
        main_organization_id = "5f850000-90a3-0025-cafa-08d89ab4828a"

        nomenclature = iiko.client.get_nomenclature(main_organization_id)
        product_id_to_article = {p.id: p.code for p in nomenclature.products}

        stop_lists = iiko.client.get_stop_list(main_organization_id)

        for stop_list in stop_lists:
            for item in stop_list.items:
                iiko_article = product_id_to_article[item.productId]
                amount_new = item.balance

                models.Product.objects.filter(iiko_id=iiko_article).update(
                    amount=amount_new
                )

                self.stdout.write(
                    self.style.SUCCESS(f"Updated {iiko_article} stock to {amount_new}")
                )

        self.stdout.write(self.style.SUCCESS("Sync stock done"))
