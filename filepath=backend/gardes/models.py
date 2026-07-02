    class Meta:
        ordering = ['date_debut']
        constraints = [
            models.UniqueConstraint(
                fields=['personnel', 'date_debut', 'date_fin'],
                name='unique_garde_overlap'
            ),
            models.CheckConstraint(
                check=models.Q(date_fin__gt=models.F('date_debut')),
                name='date_fin_apres_debut'
            ),
        ]
        