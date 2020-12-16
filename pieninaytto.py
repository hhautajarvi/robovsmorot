# TEE PELI TÄHÄN
#VERSIO PIENILLE NÄYTÖILLE
import pygame
from random import choice, randint
import time

class Pelaaja(pygame.sprite.Sprite):    #tehdään pelaajasta ja muista objekteista sprite-luokat
    def __init__(self):
        super(Pelaaja, self).__init__()     #kutsutaan spriten __init__ -metodia
        self.surf = pygame.image.load("robo.png").convert()     #ladataan oikea kuva
        self.rect = self.surf.get_rect(center=(20, 360,))   #ja tehdään kuvan muotoinen nelikulmio oikeaan paikkaan

    def liiku(self, painallukset):      #liikutetaan pelaajaa näppäinpainalluksien mukaan
        if painallukset[pygame.K_UP]:
            self.rect.move_ip(0, -4)
        if painallukset[pygame.K_DOWN]:
            self.rect.move_ip(0, 4)
        if painallukset[pygame.K_LEFT]:
            self.rect.move_ip(-4, 0)
        if painallukset[pygame.K_RIGHT]:
            self.rect.move_ip(4, 0)
        if self.rect.left <= 0:     #tarkastetaan että pelaaja pysyy kentällä
            self.rect.left = 0
        if self.rect.right >= 1280:
            self.rect.right = 1280
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= 720:
            self.rect.bottom = 720


class Vihollinen(pygame.sprite.Sprite):
    def __init__(self): 
        super(Vihollinen, self).__init__()    
        self.surf = pygame.image.load("hirvio.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(1300, randint(25, 695),))    #arvotaan vihollisten aloituskoordinaatit
        self.suunta = randint(-2, 2)    #yleimmillä tasoilla vihollisten suunta vaihtelee
        self.nopeus = randint(3, 7)     #vihollisten nopeus vaihtelee

    def liiku(self):
        self.rect.move_ip(-self.nopeus, 0)
        if self.rect.right < 0:     #poistetaan kentän ulkopuolelle menneet viholliset
            self.kill()
            return -1       #ja annetaan näistä pelaajille miinuspiste
        return 0
    
    def liiku2(self):
        self.rect.move_ip(-(self.nopeus + 2), self.suunta) #vihollinen liikkuu kakkostasolla eri suuntiin sekä nopeammin
        if self.rect.right < 0:
            self.kill()
            return -1
        if self.rect.top <= 0: #vihollinen myös kimpoaa seinistä
            self.suunta = -self.suunta
        if self.rect.bottom >= 720:
            self.suunta = -self.suunta
        return 0
    
    def liiku3(self):
        suuntalista = [-1, 0, 0, 0, 1] 
        self.suunta += choice(suuntalista) #kolmostasolla vihun suunta muuttuu jatkuvasti
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
        if self.rect.bottom >= 720:
            self.suunta = -self.suunta
        return 0

class Ammus(pygame.sprite.Sprite):
    def __init__(self, koordinaatit: tuple):
        super(Ammus, self).__init__()        
        self.surf = pygame.Surface((10, 5))     #ammus on pieni nelikulmio
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center= (koordinaatit[0], koordinaatit[1],))     #ammus lähtee pelaajan koordinaateista
        self.nopeus = 30
    
    def liiku(self):
        self.rect.move_ip(self.nopeus, 0)
        if self.rect.left > 1280:       #poistetaan kentän ulkopuolelle menneet ammukset
            self.kill()    


class Kolikko(pygame.sprite.Sprite):
    def __init__(self, koordinaatit: tuple):
        super(Kolikko, self).__init__()
        self.surf = pygame.image.load("kolikko.png").convert_alpha()
        self.rect = self.surf.get_rect(center= (koordinaatit[0], koordinaatit[1],))     #kolikko ilmestyy vihollisen koordinaatteihin


class Ovi(pygame.sprite.Sprite):
    def __init__(self):
        super(Ovi, self).__init__()
        self.surf = pygame.image.load("ovi.png").convert()
        self.rect = self.surf.get_rect(center= (-640, -480,))    #ovi odottaa pelikentän ulkopuolella

    def muuta(self): 
        self.rect = self.surf.get_rect(center= (640, 360,))     #siirretään ovi pelikentän keskelle


class Aika:         #laskuri ajalle
    def __init__(self):
        self.aloitusaika = None

    def aloita(self):
        self.aloitusaika = time.perf_counter()

    def aikanyt(self):
        return time.perf_counter() - self.aloitusaika


class Peli:     
    def __init__(self):     #asetetaan pelin aloitusarvot
        pygame.init()
        self.elossa = True
        self.aloita = True
        self.kentta2 = False
        self.kentta3 = False
        self.pisteet = 0
        self.naytto = pygame.display.set_mode((1280, 720))
        self.kello = pygame.time.Clock()    #kellolla määritetään animaation nopeus
        self.aika = Aika()
        self.lisaavihu = pygame.USEREVENT + 1
        pygame.time.set_timer(self.lisaavihu, 1500)     #määritellään kuinka usein vihollisia ilmestyy
        self.pelaaja = Pelaaja()    #lisätään kenttään pelaaja ja tasojen ovet
        self.ovi = Ovi()
        self.ovi2 = Ovi()
        self.viholliset = pygame.sprite.Group()     #laitetaan objektit omiin ryhmiinsä
        self.ammukset = pygame.sprite.Group()
        self.kolikot = pygame.sprite.Group()
        self.sprites = pygame.sprite.Group()    #yhteen ryhmään kerätään kaikki eri objektit
        self.sprites.add(self.pelaaja)
        self.fontti = pygame.font.SysFont("Arial", 24)
        pygame.display.set_caption("Robo vs Möröt")
        self.silmukka()

    def silmukka(self):
        while self.aloita:  #aloitusnäyttö näkyvillä
            self.aloitus()
        self.aika.aloita()      #aloitetaan ajan mittaus
        while self.elossa:      #suorituslooppi käynnissä
            self.tutki_tapahtumat()
            self.tutki_osumat()
            self.tutki_pisteet()
            self.piirra_naytto()
        self.lopetusaika = self.aika.aikanyt()      #lopetetaan ajan mittaus
        while True:     #lopetusnäyttö näkyvillä
            self.peli_ohi()

    def tutki_tapahtumat(self):
        for tapahtuma in pygame.event.get():      
            if tapahtuma.type == pygame.QUIT:
                exit() 
            if tapahtuma.type == self.lisaavihu:    #vihuja ilmestyy tasaisin väliajoin
                uusi = Vihollinen()
                self.viholliset.add(uusi)
                self.sprites.add(uusi)
            if tapahtuma.type == pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_ESCAPE:    #esc lopettaa pelin
                    self.elossa = False                 
                if tapahtuma.key == pygame.K_F1:    #F1 aloittaa uuden pelin
                    self.uusi_peli()      
                if tapahtuma.key == pygame.K_SPACE: #spacellä pelaaja ampuu ammuksen
                    koordinaatit = self.pelaaja.rect.center
                    ammus = Ammus(koordinaatit) 
                    self.ammukset.add(ammus)
                    self.sprites.add(ammus)
        painallukset = pygame.key.get_pressed()     #välitetään näppäinten painallukset
        self.pelaaja.liiku(painallukset)    #liikutetaan pelaajaa
        for ammus in self.ammukset: 
            ammus.liiku()   #liikutetaan ammuksia
        for vihu in self.viholliset:
            if self.kentta3:    #liikutetaan vihollisia riippuen tasosta
                piste = vihu.liiku3()
            elif self.kentta2:
                piste = vihu.liiku2()
            else:
                piste = vihu.liiku()
            self.pisteet += piste   #jos vihu pääsee vasempaan reunaan pelaaja saa miinuspisteen

    def tutki_osumat(self):
        if pygame.sprite.spritecollideany(self.pelaaja, self.viholliset): #tutkitaan osuuko pelaaja vihollisiin
            self.pelaaja.kill()
            self.elossa = False
        if not self.kentta2:
            if pygame.sprite.collide_rect(self.pelaaja, self.ovi): #tutkitaan osuuko pelaaja kakkoskentän oveen
                self.ovi.kill()
                self.viholliset.empty()     #tyhjennetään kenttä objekteista kun mennään uudelle tasolle
                self.kolikot.empty()
                self.ammukset.empty()
                self.sprites.empty()
                self.sprites.add(self.pelaaja)
                self.kentta2 = True
        if not self.kentta3:
            if pygame.sprite.collide_rect(self.pelaaja, self.ovi2): #tutkitaan osuuko pelaaja kolmoskentän oveen
                self.ovi2.kill()
                self.viholliset.empty()
                self.kolikot.empty()
                self.ammukset.empty()
                self.sprites.empty()
                self.sprites.add(self.pelaaja)
                self.kentta3 = True
        for kolikko in self.kolikot:
            if pygame.sprite.collide_rect(self.pelaaja, kolikko): #tutkitaanko osuuko pelaaja kolikkoon
                kolikko.kill()    
                if self.kentta3:    #pisteitä tulee kentän mukaan
                    self.pisteet += 3
                elif self.kentta2:
                    self.pisteet += 2
                else:
                    self.pisteet += 1
        for vihu in self.viholliset:
            for ammus in self.ammukset:
                if pygame.sprite.collide_rect(vihu, ammus): #tutkitaan osuuko ammus viholliseen
                    koordinaatit = vihu.rect.center
                    kolikko = Kolikko(koordinaatit)     #osumasta ilmestyy kolikko
                    vihu.kill()
                    ammus.kill()            
                    self.kolikot.add(kolikko)
                    self.sprites.add(kolikko)

    def tutki_pisteet(self):
        if self.pisteet == 10:  #tutkitaan aukeaako kakkostason ovi
            if not self.kentta2:
                self.ovi.muuta()
                self.sprites.add(self.ovi)
        if self.pisteet >= 30:  #tutkitaan aukeaako kolmostason ovi
            if not self.kentta3:
                self.ovi2.muuta()
                self.sprites.add(self.ovi2)
        if self.pisteet < 0:    #miinuspisteillä peli loppuu
            self.elossa = False          
        if self.pisteet >= 60:  #peli läpäisty
            self.elossa = False     

    def piirra_naytto(self):
        if self.kentta3:    #kentille on eri taustavärit
            self.naytto.fill((90, 90, 90))
        elif self.kentta2:
            self.naytto.fill((150, 150, 150))
        else:
            self.naytto.fill((211, 211, 211))
        for sprite in self.sprites:     #piirretään pelaaja ja muut objektit
            self.naytto.blit(sprite.surf, sprite.rect)
        teksti = self.fontti.render(f"Lopeta: Esc    Uusi peli: F1    Aika: {self.aika.aikanyt():0.2f}s    Pisteet: {self.pisteet}", True, (0, 0, 0))
        self.naytto.blit(teksti, (650, 20))
        pygame.display.flip()
        self.kello.tick(60)

    def peli_ohi(self):
        self.naytto.fill((211, 211, 211))
        if self.pisteet < 0:    #eri lopputekstit erilaisille lopuille
            teksti1 = self.fontti.render(f"Hävisit pelin", True, (0, 0, 0))
        elif self.pisteet >= 60:
            teksti1 = self.fontti.render(f"Onneksi olkoon, voitit pelin!", True, (0, 0, 0))
        else:
            teksti1 = self.fontti.render(f"Onnittelut, sait {self.pisteet} pistettä", True, (0, 0, 0))
        teksti2 = self.fontti.render(f"Aikasi oli {self.lopetusaika:0.2f} sekuntia", True, (0, 0, 0))
        teksti3 = self.fontti.render(f"Esc lopettaa pelin", True, (0, 0, 0))
        teksti4 = self.fontti.render(f"F1 aloittaa uuden pelin", True, (0, 0, 0))
        self.naytto.blit(teksti1, (500, 250))
        self.naytto.blit(teksti2, (500, 320))
        self.naytto.blit(teksti3, (500, 390))
        self.naytto.blit(teksti4, (500, 460))
        pygame.display.flip()
        for tapahtuma in pygame.event.get():      
            if tapahtuma.type == pygame.QUIT:
                exit()
            if tapahtuma.type == pygame.KEYDOWN:            
                if tapahtuma.key == pygame.K_ESCAPE:
                    exit()            
                if tapahtuma.key == pygame.K_F1:
                    self.uusi_peli()                   

    def aloitus(self):
        self.naytto.fill((211, 211, 211))
        fontti2 = pygame.font.SysFont("Arial", 36)
        teksti0 = fontti2.render(f"Robo vs. Möröt", True, (255, 0, 0))
        teksti1 = self.fontti.render(f"Pelin tarkoituksena on ampua ja väistellä mörköjä", True, (0, 0, 0))
        teksti2 = self.fontti.render(f"Pisteitä saat kolikoita keräämällä", True, (0, 0, 0))
        teksti3 = self.fontti.render(f"Menetät pisteen jos mörkö pääsee vasempaan reunaan", True, (0, 0, 0))
        teksti4 = self.fontti.render(f"Mörköön törmäämällä tai negatiivisilla pisteillä häviät pelin", True, (0, 0, 0))
        teksti5 = self.fontti.render(f"Ovesta pääset seuraavaan kenttään kerättyäsi tarpeeksi pisteitä", True, (0, 0, 0))
        teksti6 = self.fontti.render(f"Toisessa ja kolmannessa kentässä saat kolikoista lisäpisteitä", True, (0, 0, 0))
        teksti7 = self.fontti.render(f"60:llä pisteellä voitat pelin", True, (0, 0, 0))
        teksti8 = self.fontti.render(f"Voit liikkua nuolinäppäimillä ja ampua välilyonnillä", True, (0, 0, 0))
        teksti9 = self.fontti.render(f"Aloita peli painamalla välilyontiä", True, (0, 0, 0))
        teksti10 = self.fontti.render(f"Esc lopettaa pelin", True, (0, 0, 0))
        self.naytto.blit(teksti0, (520, 30))
        self.naytto.blit(teksti1, (350, 120))
        self.naytto.blit(teksti2, (350, 180))
        self.naytto.blit(teksti3, (350, 240))
        self.naytto.blit(teksti4, (350, 300))
        self.naytto.blit(teksti5, (350, 360))   
        self.naytto.blit(teksti6, (350, 420))   
        self.naytto.blit(teksti7, (350, 480))    
        self.naytto.blit(teksti8, (350, 540)) 
        self.naytto.blit(teksti9, (350, 600)) 
        self.naytto.blit(teksti10, (350, 660)) 
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
