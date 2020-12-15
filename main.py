# TEE PELI TÄHÄN
import pygame
from random import choice, randint

class Pelaaja(pygame.sprite.Sprite):
    def __init__(self):
        super(Pelaaja, self).__init__()
        self.surf = pygame.image.load("robo.png").convert()
        self.rect = self.surf.get_rect(center=(20, 480,))

    def liiku(self, painallukset):
        if painallukset[pygame.K_UP]:
            self.rect.move_ip(0, -5)
        if painallukset[pygame.K_DOWN]:
            self.rect.move_ip(0, 5)
        if painallukset[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)
        if painallukset[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1280:
            self.rect.right = 1280
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= 960:
            self.rect.bottom = 960


class Vihollinen(pygame.sprite.Sprite):
    def __init__(self): 
        super(Vihollinen, self).__init__()    
        self.surf = pygame.image.load("hirvio.png").convert()
        self.rect = self.surf.get_rect(center=(1300, randint(25, 935),))
        self.suunta = randint(-2, 2)
        self.nopeus = randint(3, 7)

    def liiku(self):
        self.rect.move_ip(-self.nopeus, 0)
        if self.rect.right < 0:
            self.kill()
            return -1
        return 0
    
    def liiku2(self):
        self.rect.move_ip(-(self.nopeus + 2), self.suunta)
        if self.rect.right < 0:
            self.kill()
            return -1
        if self.rect.top <= 0:
            self.suunta = -self.suunta
        if self.rect.bottom >= 960:
            self.suunta = -self.suunta
        return 0
    
    def liiku3(self):
        suuntalista = [-1, 0, 0, 0, 1]
        self.suunta += choice(suuntalista)
        if self.suunta >= 6:
            self.suunta = 5
        elif self.suunta <= -6:
            self.suunta = -5
        self.rect.move_ip(-(self.nopeus + 1), self.suunta)
        if self.rect.right < 0:
            self.kill()
            return -1
        if self.rect.top <= 0:
            self.suunta = -self.suunta
        if self.rect.bottom >= 960:
            self.suunta = -self.suunta
        return 0

class Ammus(pygame.sprite.Sprite):
    def __init__(self, koordinaatit: tuple):
        super(Ammus, self).__init__()        
        self.surf = pygame.Surface((10, 5))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center= (koordinaatit[0], koordinaatit[1],))
        self.nopeus = 30
    
    def liiku(self):
        self.rect.move_ip(self.nopeus, 0)
        if self.rect.left > 1280:
            self.kill()    


class Kolikko(pygame.sprite.Sprite):
    def __init__(self, koordinaatit: tuple):
        super(Kolikko, self).__init__()
        self.surf = pygame.image.load("kolikko.png").convert()
        self.rect = self.surf.get_rect(center= (koordinaatit[0], koordinaatit[1],))


class Ovi(pygame.sprite.Sprite):
    def __init__(self):
        super(Ovi, self).__init__()
        self.surf = pygame.image.load("ovi.png").convert()
        self.rect = self.surf.get_rect(center= (-640, -480,))    

    def muuta(self):
        self.rect = self.surf.get_rect(center= (640, 480,))


class Peli:
    def __init__(self):
        pygame.init()
        self.elossa = True
        self.aloita = True
        self.kentta2 = False
        self.kentta3 = False
        self.pisteet = 0
        self.naytto = pygame.display.set_mode((1280, 960))
        self.kello = pygame.time.Clock()
        self.lisaavihu = pygame.USEREVENT + 1
        pygame.time.set_timer(self.lisaavihu, 1500)
        self.pelaaja = Pelaaja()
        self.ovi = Ovi()
        self.ovi2 = Ovi()
        self.viholliset = pygame.sprite.Group()
        self.ammukset = pygame.sprite.Group()
        self.kolikot = pygame.sprite.Group()
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.pelaaja)
        self.fontti = pygame.font.SysFont("Arial", 24)
        pygame.display.set_caption("Robo vs möröt")
        self.silmukka()

    def silmukka(self):
        while self.aloita:
            self.aloitus()
        while self.elossa:
            self.tutki_tapahtumat()
            self.tutki_osumat()
            self.tutki_pisteet()
            self.piirra_naytto()
        while True:
            self.peli_ohi()

    def tutki_tapahtumat(self):
        for tapahtuma in pygame.event.get():      
            if tapahtuma.type == pygame.QUIT:
                exit() 
            if tapahtuma.type == self.lisaavihu:
                uusi = Vihollinen()
                self.viholliset.add(uusi)
                self.sprites.add(uusi)
            if tapahtuma.type == pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_ESCAPE:
                    self.elossa = False                 
                if tapahtuma.key == pygame.K_F1:
                    self.uusi_peli()      
                if tapahtuma.key == pygame.K_SPACE:
                    koordinaatit = self.pelaaja.rect.center
                    ammus = Ammus(koordinaatit)
                    self.ammukset.add(ammus)
                    self.sprites.add(ammus)
        painallukset = pygame.key.get_pressed()
        self.pelaaja.liiku(painallukset)
        for ammus in self.ammukset:
            ammus.liiku()
        for vihu in self.viholliset:
            if self.kentta3:
                piste = vihu.liiku3()
            elif self.kentta2:
                piste = vihu.liiku2()
            else:
                piste = vihu.liiku()
            self.pisteet += piste

    def tutki_osumat(self):
        if pygame.sprite.spritecollideany(self.pelaaja, self.viholliset):
            self.pelaaja.kill()
            self.elossa = False
        if not self.kentta2:
            if pygame.sprite.collide_rect(self.pelaaja, self.ovi):
                self.ovi.kill()
                self.viholliset.empty()
                self.kolikot.empty()
                self.ammukset.empty()
                self.sprites.empty()
                self.sprites.add(self.pelaaja)
                self.kentta2 = True
        if not self.kentta3:
            if pygame.sprite.collide_rect(self.pelaaja, self.ovi2):
                self.ovi2.kill()
                self.viholliset.empty()
                self.kolikot.empty()
                self.ammukset.empty()
                self.sprites.empty()
                self.sprites.add(self.pelaaja)
                self.kentta3 = True
        for kolikko in self.kolikot:
            if pygame.sprite.collide_rect(self.pelaaja, kolikko):
                kolikko.kill()    
                if self.kentta3:
                    self.pisteet += 3
                elif self.kentta2:
                    self.pisteet += 2
                else:
                    self.pisteet += 1
        for vihu in self.viholliset:
            for ammus in self.ammukset:
                if pygame.sprite.collide_rect(vihu, ammus):
                    koordinaatit = vihu.rect.center
                    kolikko = Kolikko(koordinaatit)
                    vihu.kill()
                    ammus.kill()            
                    self.kolikot.add(kolikko)
                    self.sprites.add(kolikko)

    def tutki_pisteet(self):
        if self.pisteet == 10:
            if not self.kentta2:
                self.ovi.muuta()
                self.sprites.add(self.ovi)
        if self.pisteet >= 30:
            if not self.kentta3:
                self.ovi2.muuta()
                self.sprites.add(self.ovi2)
        if self.pisteet < 0:
            self.elossa = False          
        if self.pisteet >= 60:
            self.elossa = False     

    def piirra_naytto(self):
        if self.kentta3:
            self.naytto.fill((90, 90, 90))
        elif self.kentta2:
            self.naytto.fill((150, 150, 150))
        else:
            self.naytto.fill((211, 211, 211))
        self.naytto.blit(self.pelaaja.surf, self.pelaaja.rect)
        for sprite in self.sprites:
            self.naytto.blit(sprite.surf, sprite.rect)
        teksti = self.fontti.render(f"Lopeta: Esc    Uusi peli: F1    Pisteet: {self.pisteet}", True, (0, 0, 0))
        self.naytto.blit(teksti, (850, 20))
        pygame.display.flip()
        self.kello.tick(60)

    def peli_ohi(self):
        self.naytto.fill((211, 211, 211))
        if self.pisteet < 0:
            teksti1 = self.fontti.render(f"Hävisit pelin", True, (0, 0, 0))
        elif self.pisteet >= 60:
            teksti1 = self.fontti.render(f"Onneksi olkoon, voitit pelin!", True, (0, 0, 0))
        else:
            teksti1 = self.fontti.render(f"Onnittelut, sait {self.pisteet} pistettä", True, (0, 0, 0))
        teksti2 = self.fontti.render(f"Esc lopettaa pelin", True, (0, 0, 0))
        teksti3 = self.fontti.render(f"F1 aloittaa uuden pelin", True, (0, 0, 0))
        self.naytto.blit(teksti1, (350, 300))
        self.naytto.blit(teksti2, (350, 370))
        self.naytto.blit(teksti3, (350, 440))
        pygame.display.flip()
        for tapahtuma in pygame.event.get():      
            if tapahtuma.type == pygame.QUIT:
                exit()
            if tapahtuma.type == pygame.KEYDOWN:            
                if tapahtuma.key == pygame.K_ESCAPE:
                    exit()
            if tapahtuma.type == pygame.KEYDOWN:            
                if tapahtuma.key == pygame.K_F1:
                    self.uusi_peli()                   

    def aloitus(self):
        self.naytto.fill((211, 211, 211))
        teksti1 = self.fontti.render(f"Pelin tarkoituksena on ampua ja väistellä mörköjä", True, (0, 0, 0))
        teksti2 = self.fontti.render(f"Pisteitä saat kolikoita keräämällä", True, (0, 0, 0))
        teksti3 = self.fontti.render(f"Menetät pisteitä jos mörkö pääsee vasempaan reunaan", True, (0, 0, 0))
        teksti4 = self.fontti.render(f"Mörköön törmäämällä tai negatiivisilla pisteillä häviät pelin", True, (0, 0, 0))
        teksti5 = self.fontti.render(f"Ovesta pääset seuraavaan kenttään kerättyäsi tarpeeksi pisteitä", True, (0, 0, 0))
        teksti6 = self.fontti.render(f"Toisessa ja kolmannessa kentässä saat kolikoista lisäpisteitä", True, (0, 0, 0))
        teksti7 = self.fontti.render(f"60:llä pisteellä voitat pelin", True, (0, 0, 0))
        teksti8 = self.fontti.render(f"Voit liikkua nuolinäppäimillä ja ampua välilyonnillä", True, (0, 0, 0))
        teksti9 = self.fontti.render(f"Aloita peli painamalla välilyontiä", True, (0, 0, 0))
        teksti10 = self.fontti.render(f"Esc lopettaa pelin", True, (0, 0, 0))
        self.naytto.blit(teksti1, (350, 50))
        self.naytto.blit(teksti2, (350, 120))
        self.naytto.blit(teksti3, (350, 190))
        self.naytto.blit(teksti4, (350, 260))
        self.naytto.blit(teksti5, (350, 330))
        self.naytto.blit(teksti6, (350, 400))   
        self.naytto.blit(teksti7, (350, 470))   
        self.naytto.blit(teksti8, (350, 540))    
        self.naytto.blit(teksti9, (350, 610)) 
        self.naytto.blit(teksti10, (350, 680)) 
        pygame.display.flip()
        for tapahtuma in pygame.event.get():      
            if tapahtuma.type == pygame.QUIT:
                exit()
            if tapahtuma.type == pygame.KEYDOWN:            
                if tapahtuma.key == pygame.K_SPACE:
                    self.aloita = False
                if tapahtuma.key == pygame.K_ESCAPE:
                    exit()

    def uusi_peli(self):
        Peli()
Peli()
